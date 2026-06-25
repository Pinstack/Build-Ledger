---
review: adversarial-divergence
spine: ARCHITECTURE-SPINE.md
target: Build Ledger v1
reviewer-gate: divergence (one level down)
date: '2026-06-25'
verdict: HOLES-FOUND
---

# Adversarial Divergence Review — Build Ledger Spine

**Method.** I am the adversary at the Reviewer Gate. I take two units exactly **one level down** from the spine — any two of the seven Collector Modules (`repos`, `coauthorship`, `artefacts`, `practice`, `retrospective`, `in_flight`, `redaction`), the **Collector vs the Generated Page**, or **two future builders of the same Module** — and I make each one obey **every** AD to the letter. Then I show them building artifacts that **cannot compose**: clashing data shapes, two owners of one entity, conflicting mutation/redaction order, an unpinned key type/unit, or an open idempotency/ordering assumption. Each surviving pair is a hole the spine must close with a new or tightened AD. I am not raising taste objections; every item below is a specific pair that passes the current text and still breaks the build.

The spine is unusually disciplined on the *privacy membrane* (AD-4/5/6) and the *contract-as-only-coupling* stance (AD-2). The holes are not there. They are in **ownership of the shared `repositories[]` element and `aggregates`**, in **run atomicity/idempotency**, in **the under-specified prohibited-field list vs. free text**, and in **a handful of unpinned key shapes** the Page and a Module are each free to interpret differently. Twelve ADs is a strong spine; it is missing roughly four invariants and three rule-tightenings.

---

## CRITICAL HOLES

### H1 — `repositories[]` has one *key* owner but **three** *writers*; AD-3's "sole writer" is false as written
**The pair:** `repos.py` and `coauthorship.py` (also `artefacts.py`), each fully AD-3-compliant.

**The contradiction in the spine's own text.** AD-3 Rule: *"each Module owns exactly **one** top-level key and is the only writer of it; no Module reads or writes another's key."* But the Capability → Architecture Map assigns:
- `modules/repos.py` → `repositories[]`, `aggregates`
- `modules/coauthorship.py` → `repositories[].coauthorship`
- `modules/artefacts.py` → `repositories[].ai_artefacts`

`coauthorship` and `ai_artefacts` are **sub-objects of array elements inside the `repositories` top-level key that `repos.py` owns.** Three Modules write into the same array-of-objects. "Owns one top-level key and is the only writer of it" is literally violated for `repositories`, and the spine never says how `repositories[]` row objects are *assembled* from three independent writers.

**The concrete incompatible build.** Two AD-compliant builders, both told "you own your slice of `repositories[]`":
- `repos.py` builder decides a repo row is **keyed by position in a list it discovers and sorts by commit count**, and emits `repositories` as a fully-formed list with `coauthorship`/`ai_artefacts` left as `null` placeholders for the others to fill.
- `coauthorship.py` builder decides it will **emit its own list of `{id, coauthorship}` objects** and expects the Collector to *merge by `id`*. It sorts by repo name. It also has its own opinion of which repos exist (it only saw repos that have any commits at all; a freshly-created empty repo `repos.py` included is absent from coauthorship's list).

Now the Collector must reconcile two lists of different length, different order, different membership, joined on an `id` whose generation rule is **also unowned** (see H4). One builder's row 7 is the other builder's row 4; a repo present in `repos[]` has no `coauthorship` entry; a merge-by-id silently drops or null-fills. The file is internally inconsistent and **no AD was broken**. This is the "two owners of one entity" hole, and it is the single most likely thing to actually break the v1 build because the hero figure (coauthorship) and the volume figures (repos) are produced by different files that must align row-for-row.

**Fix — new AD-13 (Row assembly & single-writer-per-field):**
> `repositories[]` is **assembled by `collect.py` alone** from a single canonical repo set. `repos.py` is the **sole producer of the repo set and of each row's identity, `display_tier`, `allowlisted`, `metrics`, `signals`** (the "spine" of the row). Every other Module that contributes to a row (`coauthorship`, `artefacts`, future) is a **field-level contributor**: it receives the canonical repo set (id-list) as input and returns a **map keyed by repo `id`** carrying **only its own named sub-key** (`coauthorship`, `ai_artefacts`). `collect.py` left-joins these maps onto the canonical rows by `id`; a contributor that returns no entry for a canonical `id` yields that sub-key's **explicit empty/`available:false` form, never a missing key or a dropped row.** No contributor may add, drop, or reorder rows, or write any field outside its named sub-key. AD-3's "one writer per key" is hereby refined to **one writer per *field path*** (top-level key, or named sub-key within `repositories[]`), with `collect.py` as the sole assembler of the array itself.

This makes "who owns the row vs. who owns a cell" explicit and turns the join key + membership into a contract rather than a coincidence.

---

### H2 — `aggregates` is owned by `repos.py` but its contents are **cross-cutting totals that require other Modules' logic** — two owners of one number
**The pair:** `repos.py` (owns `aggregates`) vs `coauthorship.py` (owns the human/agent split).

**The hole.** `aggregates.totals` is specified as `{ "commits", "user_authored_commits", "loc_net" }`, and `aggregates` is assigned solely to `repos.py`. But `user_authored_commits` is a **co-authorship concept** — it is "commits authored by the human, not an agent or excluded bot," which is *exactly* the partition `coauthorship.py` computes per repo (`human_commits` vs `agents[]` vs `excluded_bots[]`). So:
- `repos.py` builder computes `user_authored_commits` by its **own** definition of "user-authored" (say: commits whose git `author` is the human identity, ignoring trailers).
- `coauthorship.py` builder computes `human_commits` per repo by a **different** definition (say: commits with no agent `Co-authored-by:` trailer, regardless of author field; or excluding `dependabot` from the denominator differently).

Sum the per-repo `coauthorship.human_commits` and you get a number that **disagrees** with `aggregates.totals.user_authored_commits`. Both Modules are AD-compliant (each wrote only its own key). The Page now shows a headline split that doesn't reconcile against the per-repo evidence a skeptic (UJ-2, Sam) drills into — which is *precisely the failure mode the whole product exists to avoid* (SM-2/SM-4: "a skeptic finds the number that doesn't add up"). Two owners, one quantity, no single definition.

The same defect hits `aggregates.totals.commits` vs `Σ repositories[].metrics.commits`, and `aggregates.repo_counts` vs the `display_tier`/`status` fields on the rows, and `aggregates.languages` (does it include or exclude the excluded files of the Excluded-from-counts Note? `repos.py` and a future `aggregates` builder can each decide).

**Fix — new AD-14 (Aggregates are derived, never independently computed):**
> `aggregates` is a **pure projection of already-emitted per-row fields**, computed by `collect.py` **after** all Modules have produced their rows, by a **specified reduction** — not independently recomputed by any Module from raw sources. Every aggregate field names its source field path and reduction: `totals.commits = Σ repositories[].metrics.commits`; `totals.user_authored_commits = Σ repositories[].coauthorship.human_commits` (so the headline split is, by construction, the sum of the rows the skeptic inspects); `repo_counts.* = count(repositories[] by display_tier/status)`; `languages[].share` is computed from the **same post-exclusion LOC** that feeds `metrics.loc_net`. No Module other than the assembler writes `aggregates`. If a needed per-row field does not exist, the aggregate that depends on it is omitted (with the Module's `available:false`), never independently re-derived. This guarantees page-level totals reconcile against row-level evidence — the core auditability NFR.

---

### H3 — Run atomicity / partial-failure is **undefined**: a mid-run Module crash can publish a half-old/half-new file (or no rule says it can't)
**The pair:** Collector run N (all Modules succeed) vs Collector run N+1 (`practice.py` throws *after* `repos.py`/`coauthorship.py` have written, *before* `redaction.py` runs) — or the Page reading whichever file lands.

**The hole.** The spine says state is "immutable per run — each run emits a fresh `build-ledger.json`; never edited in place," and "a Module error → its `available: false`." These two rules **conflict at the seam** and leave the failure path open:
- "A Module error → `available:false`" implies the run **continues** and publishes with that Module degraded.
- But *which* errors are catchable-to-`available:false` vs. fatal-to-the-run is unspecified. A Module that throws a raw exception (network blip mid-`gh` call, a `tokei` segfault, a `KeyError` on a malformed log) does **not** politely set its own flag — it crashes the process.

So two compliant builders diverge:
- Builder A wraps every Module in `try/except → available:false` and **always publishes** something. Result: a transient GitHub outage silently ships a file where half the repos have `commits: 0` and `available:false`, the heatmap collapses, and the published-beside-the-page file (AD-8) now *is* the misleading artifact a skeptic catches.
- Builder B lets exceptions propagate and **aborts**, leaving the **previous** `public/build-ledger.json` in place (it's the deploy target). Now the Page shows last week's data with **this week's `ledger_metadata.generated_at`** if metadata was written first — or a torn file if the writer is not atomic.

Worse, the **write itself** is unspecified as atomic. If `collect.py` streams JSON to `public/build-ledger.json` in place and dies mid-write, the deployed file is **truncated** → the Page (or a reader's `JSON.parse`) breaks under inspection (fails FR-10/SM-4 directly). Nothing in the spine forbids in-place streaming to the served path.

There is also no **idempotency** statement: re-running the Collector twice on an unchanged working tree should yield byte-identical `build-ledger.json` (modulo `generated_at`). Without it, two runs minutes apart can differ (e.g. dict iteration order, language tie-break, float formatting), and the **git history of `public/build-ledger.json` — which AD's structural seed calls "the provenance trail"** — fills with spurious diffs, undermining the very provenance claim.

**Fix — new AD-15 (Atomic, all-or-nothing, idempotent run):**
> A run computes the **entire** `build-ledger.json` in memory (or a temp path in the private drawer), passes the AD-4 whole-document assert, and only then **atomically replaces** the served `public/build-ledger.json` (write-temp-then-`os.replace`). A run **never** mutates the served file in place and **never** leaves it torn. Distinguish two failure classes: **(a) Module-degraded** — a Module that cannot produce data sets `available:false` (or per-row empty form) and the run proceeds; **(b) Run-fatal** — any *uncaught* Module exception, a schema-invalid assembled document, or a failed redaction assert aborts the **whole** run, publishes **nothing**, and leaves the prior file and its `generated_at` untouched (fail-closed, consistent with AD-4 and the Safety rule). The boundary between (a) and (b) is explicit: a Module declares its **expected** empty state (the FR-5 "no logs → no data this run" path is class (a)); an **unexpected** throw is class (b). Runs are **deterministic/idempotent**: given the same inputs (clones, logs, config) the emitted bytes are identical except `ledger_metadata.generated_at` — Modules must sort all collections by a **stable documented key** and format floats canonically (3 dp, fixed), so the provenance git-history carries only real changes.

This closes "half-old/half-new," "torn file," "degraded vs fatal," and "noisy provenance trail" in one invariant.

---

## HIGH HOLES

### H4 — Repo `id` is "stable opaque string" with **no generation rule** — two builders mint incompatible ids, and the join in H1 silently fails
**The pair:** `repos.py` builder this quarter vs `repos.py` builder next quarter (two future builders of the **same** Module) — and the cross-Module join of H1.

**The hole.** Conventions say `Repo id: stable opaque string`. "Stable" across **what**? Two compliant builders:
- Builder A: `id = sha1(github_repo_node_id)` — stable across renames, unique, opaque. Good.
- Builder B: `id = slugified repo name` or `id = array index` or `id = sha1(local clone path)`.

Each satisfies "stable opaque string." But **(i)** a name-derived or path-derived id **leaks** under a naive read and, more importantly, **changes when the client renames the repo or the clone moves** — so the id is *not* stable run-to-run, which means the Page cannot correlate a repo across weekly snapshots (kills any future momentum/trend view and even this-week's "did repo X change" diffing), and **(ii)** the H1 cross-Module join breaks the moment `coauthorship.py`'s builder and `repos.py`'s builder derive the id from different inputs (one from GitHub node id, one from clone path → **no key matches**, every row gets null coauthorship). Also: for an `aggregate_only` Silhouette, is the id derived from the **private name**? If so it's a weak hash-leak (a determined reader with a guessed repo name can confirm presence by recomputing the hash) — an under-the-radar redaction concern.

**Fix — tighten the Naming convention (amend Consistency Conventions + AD-3/AD-13):**
> Repo `id` is defined as a **stable, non-reversible** identifier derived from the GitHub **repository node id** (immutable across renames/moves), e.g. `id = base32(hmac_sha256(key=run-constant-salt, msg=github_node_id))[:16]`. It is **not** derived from the repo name, file path, or list position. The salt is a fixed repo-constant (not per-run) so ids are stable across runs; it is documented as non-secret. The **single** id-generation function lives in `repos.py` and is the only id source; all other Modules receive ids from the canonical set (H13) and never mint their own. For Silhouettes the same node-id basis is used so the id carries no client string and cannot be confirmed by hashing a guessed name (the HMAC salt defeats the dictionary check).

### H5 — The prohibited-field list is a **value blocklist with no field-level allowlist**; a Module emits a client name in a free-text field that "passes" because the assert can't know it's a name
**The pair:** `practice.py` (writes `cost.confounders: ["<named confounder>"]`) or `retrospective.py` (writes `window_view: []`) vs `redaction.py`.

**The hole.** AD-4 asserts "none of the prohibited fields appear" over the whole document, and FR-6 lists the prohibited *categories*: repo name, file path, branch, commit message, client name, proprietary project name, secret, transcript. But **how does the assert detect a "client name" in arbitrary free text?** A client name is not a syntactic pattern. Concretely:
- `practice.py` builder, obeying every AD (aggregate-only, no transcripts), writes a confounder string: **`"cost rose during the Client A migration sprint"`** — an aggregate, scripted, no transcript, no path. It names a client in free text. The redaction assert, which can reliably catch *known* private repo names/paths (it has the repo list) and `sk-…`/token regexes, has **no list of client names** (the Allowlist is empty and client names were deliberately *not* enumerated per the resolved Open-Q — "no per-repo review needed because everything is a Silhouette"). The string passes. A client name ships. **AD-4 is satisfied to the letter and the leak occurs.**
- Symmetrically, `retrospective.window_view` is sourced from BMAD memlogs (planning prose). A window-view bullet **"shipped the Client B search rebuild"** is curated, source-bound, contains no repo name/path — and names a client.

The spine even *flags* the free-text confounders as the risk ("especially the free-text `cost.confounders` notes") but the **mechanism** to neutralize them is missing: the assert is a denylist of strings it *happens to know*, and the most dangerous strings (client names in prose) are exactly the ones it does not know.

**Fix — tighten AD-4 (free-text is allowlist-shaped, not denylist-scanned):**
> Redaction over **free-text-bearing fields** (`agentic_practice.cost.confounders`, `retrospective.window_view`, `in_flight` labels, `aggregates.languages[].name`, `model_mix` labels) is **allowlist-by-construction, not denylist-by-scan**: these fields may contain **only** values drawn from a **controlled vocabulary** declared in `config/redaction.yml` (e.g. confounders ∈ {`model_price_change`, `project_mix_shift`, `cache_warmup`, …}; languages ∈ tokei's language set; model names ∈ `ai_sources.yml`). Any value **not** in the vocabulary fails the assert (fail-closed). Modules that would emit prose (`retrospective.window_view`) must emit **structured, vocabulary-bound** entries (e.g. `{theme: <enum>, metric: <number>}`) — **never raw memlog sentences** — so "a client name in prose" is structurally impossible rather than scanned-for. The denylist of *known* private strings (repo names, paths, the human's own non-public identity, secret regexes) remains as a second, belt-and-suspenders layer over the **whole** document. The Methodology Note states that free-text fields are vocabulary-bound.

This converts the redaction gate from "catch the bad string" (unwinnable for client names) to "permit only known-safe values" (decidable).

### H6 — Redaction vs aggregate-computation **ordering** is unpinned; a tier change after aggregation makes counts and rows disagree
**The pair:** `redaction.py` vs `repos.py`/`collect.py` (aggregation), and the order `collect.py` runs them.

**The hole.** AD-4 says redaction runs "before publish" as a single whole-document pass. AD-14 (proposed) says aggregates are derived after rows. But the spine pins **neither** the order of *redaction relative to aggregation* nor *redaction relative to row assembly*. Two compliant builders:
- Builder A: assemble rows → compute `aggregates` → **then** redact (redaction may blank `label`s, drop `attribution`, coerce a row to Silhouette). Now `aggregates.repo_counts.public` was computed **before** a repo that failed an allowlist check got demoted to `aggregate_only` → the public count is **one too high** and disagrees with the rows. The skeptic counts rows and catches it.
- Builder B: redact rows → compute aggregates from redacted rows. Counts reconcile, but now if redaction is what *sets* `display_tier`, a Module that computed `metrics` on the pre-redaction repo and an aggregate computed post-redaction can still diverge on LOC if redaction zeroes a Silhouette's `loc_net` (does it? unspecified — see H8).

Because redaction **mutates** the document (it is the one sanctioned state-mutation path) and aggregation **reads** it, their relative order changes the published numbers. Nothing says which runs first.

**Fix — tighten AD-4 + AD-14 (pin the pipeline order):**
> The run order is **fixed and documented**: (1) `repos.py` produces the canonical repo set with `display_tier`/`allowlisted` already resolved from config (tiering is an **input decision**, not a redaction-time mutation); (2) field-contributor Modules fill their sub-keys; (3) `collect.py` derives `aggregates` from the assembled rows; (4) the **redaction pass** runs over the whole document as the **final transform before the assert**, and is **assertion-only on already-tier-correct data** — it may *verify and blank stray identifying strings* but must **not** change a repo's `display_tier` or membership (if tiering were wrong, that is a **run-fatal** config error, not a silent demotion). Therefore aggregates and rows are computed from the *same* tier decisions and always reconcile. The ordering is part of the contract, not a builder's choice.

---

## MEDIUM HOLES

### H7 — Empty/absence is specified **three incompatible ways**; the Page can't tell "no data" from "zero" from "absent"
**The pair:** `practice.py` / `retrospective.py` / `in_flight.py` (three Modules, three absence conventions) vs the Generated Page.

**The hole.** AD-3 says a Module with no data emits `available: false` with empty sub-objects. But the contract shows **at least three** different shapes for "nothing," and not every key has an `available` flag:
- `agentic_practice` has an explicit `available` boolean. Good.
- `retrospective` has **no** `available` flag — just `window_view: []`. Is an empty array "no retrospective this run" or "a run that genuinely had nothing to say"?
- `in_flight` has **no** `available` flag and is a flat object of integers (`wip_branches: 0`…). Is `0` "no WIP" or "module couldn't read the repos"?
- A per-row `coauthorship` with `human_commits: 0, agents: []` — is that "a repo with no commits" or "coauthorship module failed for this repo"?

Two compliant Module builders pick opposite conventions (one uses `available:false`, one uses empty-collection-means-absent), and the Page builder — reading "solely from the file" (AD-2) — **cannot distinguish degraded from genuinely-zero**, so it either renders a misleading "0 WIP branches / 0% AI" (looks like a real finding) when the truth is "we couldn't measure," or it hides a real zero. Both violate the spirit of FR-8's "represent missing explicitly, don't guess" while satisfying AD-3's letter (which only *mentions* `available:false`, doesn't *require* it on every top-level key).

**Fix — tighten AD-3 (uniform availability envelope):**
> **Every** top-level Module key carries the **same availability envelope**: an `available: true|false` field is **mandatory** on `agentic_practice`, `retrospective`, `in_flight`, and on the per-row `coauthorship` and `ai_artefacts` contributions. `available:false` means "not measured this run" and pairs with empty/`null` payload; `available:true` with all-zero payload means "measured, genuinely zero." The Page renders `available:false` as an explicit "no data this run" state and **never** as a numeric finding. A bare empty collection is **not** a valid absence signal anywhere. (This generalizes the existing `agentic_practice.available` to a document-wide rule.)

### H8 — What a Silhouette row's **numeric fields** contain is unspecified — `metrics`/`signals` for `aggregate_only` are an open shape
**The pair:** `repos.py` builder A vs builder B, both rendering a private repo as a Silhouette.

**The hole.** The Glossary says a Silhouette is "shape and signals only (counts, presence of tests/CI), no identifying strings." The redaction contract says for `aggregate_only` "only `metrics`/`signals`/aggregate `coauthorship` counts appear." But it never says **which** metrics survive. Is `loc_net` a "count" (allowed, it's a number) or an "identifying" signal (a 2.3M-LOC repo is near-uniquely identifiable among ~35 clients)? Two builders:
- Builder A keeps **full `metrics`** on Silhouettes (commits, loc_net, active_days) — "they're just numbers." A reader cross-references "the 2.3M-LOC private repo with 4,000 commits" against public knowledge of a known client engagement and **re-identifies** it. Redaction "passed" (no string leaked) yet the Silhouette is effectively named by its measurements.
- Builder B zeroes or buckets Silhouette metrics. Now `aggregates.totals.commits` (Σ rows) **disagrees** with reality and with builder A's file; the two Collectors emit different totals for the same repos.

So the *value-level* redaction policy for Silhouettes is open, and it interacts with H2 (aggregates) — whether Silhouette metrics are full, bucketed, or zeroed changes the published totals, and two compliant builders pick differently.

**Fix — new AD-16 (Silhouette numeric policy is pinned):**
> For `display_tier: aggregate_only`, the row carries `signals` (booleans) and `coauthorship` **ratios** in full, but **magnitude metrics** (`metrics.commits`, `loc_*`, `active_days`) are emitted **bucketed to coarse ranges** from a fixed scale in `config/redaction.yml` (e.g. LOC ∈ {`<1k`,`1–10k`,`10–100k`,`>100k`}), never raw, so a Silhouette cannot be re-identified by a near-unique measurement. `aggregates.totals` are computed from **public+redacted rows' raw metrics plus Silhouette rows' bucket midpoints (or are explicitly scoped to public repos and labelled as such)** — the chosen rule is documented so every builder produces the same totals. The Methodology Note states that Silhouette magnitudes are bucketed.

*(If the project prefers raw Silhouette metrics, the fix is the same shape — pick one rule and pin it — but bucketing is the safer default given ~35 real clients and the re-identification risk.)*

### H9 — `collector_version` and `schema_version` ownership/agreement is unpinned; the file can self-contradict
**The pair:** `collect.py` (writes top-level `schema_version` and `ledger_metadata.collector_version`) vs any Module that "knows" the schema it emits, and the Page reading two `schema_version` copies.

**The hole.** `schema_version` appears **twice** (top-level and inside `ledger_metadata`), and the Page is told to "read `schema_version` first" (AD-7) — but **which copy**? Nothing asserts the two are equal. A builder updates one and not the other; the Page reads the top-level `1.1.0` and renders v1.5 features while `ledger_metadata.schema_version` (the one displayed, per the PRD) still says `1.0.0`. Likewise `collector_version` is free-form `<semver>` with no owner stated and no rule tying it to the actual emitting code, so the audit header (a core FR-9 trust cue) can lie without any AD firing.

**Fix — tighten AD-7 + Conventions:**
> `collect.py` is the **sole** writer of `schema_version` (both occurrences) and `collector_version`, and **asserts the two `schema_version` copies are byte-equal** as part of the AD-15 schema validation (a mismatch is run-fatal). The Page reads the **`ledger_metadata.schema_version`** (the displayed one) as authoritative and ignores the top-level duplicate beyond the equality check. `collector_version` is bound to the Collector's own released version (single source), never hand-set per Module.

### H10 — `agentic_practice` sub-shapes (`cadence`, `model_mix`, `cost.trend`) are emitted as bare `{}`/`[]` — two builders pick incompatible element shapes the Page can't render
**The pair:** `practice.py` builder A vs builder B (two future builders of the same Module) vs the Page.

**The hole.** The contract gives `cadence: {}`, `model_mix: []`, `cost.trend: []` with **no element schema**. Two compliant builders:
- `model_mix`: builder A emits `[{"model":"opus","share":0.4}]`; builder B emits `[{"name":"claude-opus-4","sessions":120}]`. Different keys, different semantics (share vs count), different model-label vocabulary (`opus` vs `claude-opus-4`). The Page hard-codes one and breaks (or silently renders blank) on the other — under inspection (FR-10). The model-label vocabulary also feeds redaction (H5): an un-pinned label set can't be allowlisted.
- `cost.trend`: builder A emits `[{"week":"2026-W24","usd":12.3}]`; builder B emits `[[1719273600, 12.3]]`. Both "a trend." Page can't consume both.
- `cadence`: `{}` is wide open — `{"sessions_per_week":…}` vs `{"by_day":{…}}`.

AD-2 makes the file the *only* coupling, which makes these unpinned shapes **load-bearing**: an unpinned element schema is an unpinned contract, and the Page↔Module pair diverges with zero AD violation.

**Fix — new AD-17 (No open containers in the contract):**
> Every container in `build-ledger.json` has a **pinned element schema** in the contract (or a companion schema file): `model_mix[]` = `{model: <enum from ai_sources.yml>, share: <float 0–1, 3dp>}`; `cost.trend[]` = `{period: <ISO-8601 week or date>, usd: <number>, pricing_source: <label>}`; `cadence` = `{sessions_per_week: <number>, active_days: <number>}` (or a named, documented object). `commit_trajectory[]` and `languages[]` likewise. A bare `{}`/`[]` with no element schema is **not** a valid contract field. The element vocabularies (models, confounders, languages) are the **same** controlled vocabularies the redaction allowlist (H5) uses, so "renderable by the Page" and "passable by redaction" are the same constraint.

---

## LOW / SEAMS

### H11 — Float formatting and rounding are stated as a *display* convention, not a *serialization* invariant — idempotency (H3) and cross-builder agreement leak through the last decimal
**The pair:** any two Modules emitting ratios, or two runs.
Conventions say "Shares/ratios: floats 0–1, 3 dp." But JSON has no fixed-precision float; `0.614` may serialize as `0.6140000000000001` depending on the path, and "3 dp" could be round-half-up vs round-half-even, or applied at display vs at emit. Two builders disagree in the third decimal; the published file's git diff (the provenance trail) churns; the hero `~61.4%` becomes `61.3%` vs `61.4%` across runs.
**Fix:** state in Conventions that ratios are serialized as **strings or fixed-3dp numbers via a single canonical formatter** (round-half-even, applied at emit, not display), shared by all Modules — folded into the AD-15 determinism rule.

### H12 — `excluded_bots` membership vs `aggregates.totals` denominator is unpinned (the dependabot question)
**The pair:** `coauthorship.py` (classifies an author as `agents[]` vs `excluded_bots[]`) vs `repos.py`/aggregation (`user_authored_commits`, `totals.commits`).
FR-3 says bot-noise (dependabot) must be *distinguishable* from genuine agents, and both appear in the row. But whether `excluded_bots` commits are **in or out** of `aggregates.totals.commits` and of the `metrics.commits` denominator is unspecified. Builder A counts dependabot commits in `totals.commits`; builder B excludes them (they're in the Excluded-from-counts Note's "bot-authored commits"). The headline AI share (numerator agents / denominator commits) shifts depending on whether the denominator includes excluded bots — two compliant builders publish different hero percentages.
**Fix:** pin in the Methodology/Conventions that `excluded_bots[].commits` are **excluded** from every headline denominator (`metrics.commits`, `aggregates.totals.commits`, the coauthorship denominator) and surfaced **only** as a side count; the Excluded-from-counts `bot_commits` total **equals** Σ `excluded_bots[].commits` (one definition, reconcilable). Fold into AD-14.

### H13 — `config/*.yml` is shared mutable input across all seven Modules with no schema/owner — a silent cross-cutting coupling outside the file
**The pair:** `redaction.py` (reads `redaction.yml`, `repos.yml`) vs `repos.py` (reads `repos.yml`, `exclusions.yml`) vs `practice.py` (reads `ai_sources.yml`, `pricing.yml`).
AD-2 says the **file** is the only coupling between Collector and Page — true. But **inside** the Collector, the `config/*.yml` set is a shared input multiple Modules read, and the spine never says **who owns/validates each config's schema**. Two Modules can read `repos.yml` expecting different shapes (repos.py wants discovery filters; redaction.py wants per-repo tier), or `ai_sources.yml`'s model vocabulary (which both practice's `model_mix` and redaction's allowlist depend on, per H5/H10) can be defined by one and misread by the other. This is a real "hidden coupling" the membrane metaphor misses because it's *upstream* of the file.
**Fix:** add a Convention that each `config/*.yml` has **one owning Module that defines and validates its schema** at run start (fail-closed on malformed config — a class-(b) run-fatal per H3), and shared vocabularies (`ai_sources.yml` model names) are validated once and **passed** to consumers, not independently re-parsed. State the owner per file in the Capability map.

### H14 — `display_tier: "redacted"` is "representable but unused" in v1 — a latent shape with no producer and a Page branch nothing exercises
**The pair:** the Page builder vs reality.
The contract permits `display_tier ∈ {public, redacted, aggregate_only}` and `label` semantics differ per tier, but v1 ships **only** `public` and `aggregate_only` (empty Allowlist). A Page builder must still write a `redacted` rendering branch (the enum allows it) that **no v1 file ever exercises** → dead, untested code path that may be wrong the first time a repo is promoted. Minor, but it's a divergence-in-waiting between the contract's allowed space and the producible space.
**Fix (low):** note in the contract that v1 producers emit **only** `public`/`aggregate_only`; the Page **must** still handle `redacted` (forward-compat) but that branch is explicitly marked "untested until first promotion" so it's reviewed when the Allowlist gains its first entry. Optional: have the redaction self-test fixture include a synthetic `redacted` row so the Page branch is exercised.

---

## What the spine already closes (so the gate is fair)
- **Mirror leak** (AD-6) — machine-checkable "no `retrospective.mirror_view` key" is genuinely tight; the two-artifact split is correct.
- **Private data in the tree** (AD-5) — the drawer-outside-the-tree construction is structural, not discipline-based. Good.
- **Page reaching past the file** (AD-2/AD-8) — "renders solely from the file," published-beside-the-page, build-time static. The Collector↔Page seam is well-pinned *except* where the file's shapes are open (H7, H10) — i.e. the coupling is right but the contract is under-typed.
- **Schema evolution** (AD-7) — additive-MINOR / breaking-MAJOR with the `attribution` worked example is sound; H9 only tightens *who writes the version and that the two copies agree*.

## Verdict & priority
**HOLES-FOUND.** The privacy membrane and the one-file-coupling stance are strong; the divergence surface is **(1) shared ownership of `repositories[]`/`aggregates`**, **(2) run atomicity/idempotency**, **(3) redaction-of-free-text and its ordering vs aggregation**, and **(4) a cluster of unpinned key shapes/units.** Close in this order:

1. **H1 + H2 (+H4, H12)** — assembler-owns-the-array, fields-have-single-writers, aggregates-are-derived, id-rule pinned. *This is the build-breaker.* → **AD-13, AD-14.**
2. **H3 (+H11)** — atomic, all-or-nothing, idempotent run. → **AD-15.**
3. **H5 + H6** — free-text is vocabulary-bound; redaction-after-aggregation order pinned; tiering is an input not a redaction mutation. → tighten **AD-4**.
4. **H7, H8, H9, H10 (+H13, H14)** — uniform availability envelope, Silhouette numeric policy, version single-writer+equality, no-open-containers, config ownership. → tighten **AD-3/AD-7**, add **AD-16/AD-17**.

Four new ADs (13–17, counting the AD-4/AD-3/AD-7 tightenings) take this from "strong spine with seams two builders fall through" to "a future builder cannot build an incompatible Module off compliant code."
