---
title: Reconciliation Review — Addendum → Architecture Spine
type: architecture-review
mode: reconcile-addendum
reviewer: reconciliation-reviewer
created: 2026-06-25
verdict: MINOR GAPS
inputs:
  spine: architecture/architecture-Build-Ledger-2026-06-25/ARCHITECTURE-SPINE.md
  addendum: briefs/brief-Build-Ledger-2026-06-24/addendum.md
  cross-ref-prd: prds/prd-Build-Ledger-2026-06-24/prd.md
---

# Reconciliation Review — Addendum → Architecture Spine

## Scope & method

The addendum holds **all** technology-stack and architecture-how detail (the PRD explicitly delegates it there). This review reads the addendum as the source of load-bearing technical constraints and checks each against the **terse** ARCHITECTURE-SPINE. A finding is logged **only** where the addendum names something load-bearing that two independently-built units could diverge on, and the spine does **not** fix it, convention-ize it, map it, or defer it. Build-detail correctly owned by code is **not** flagged.

The PRD is bound by the spine (`companions`, `sources`) and is consulted as a mitigant: where the spine omits something but its bound companion fixes it concretely, the finding is downgraded (the constraint is anchored *somewhere the spine points to*), not dismissed (the spine's own map still falls short of its stated job — "the durable heart a future builder can't read off compliant code").

**Verdict: MINOR GAPS.** No invariant is left wholly unfixed across the spine + its bound PRD, and the AD-4 whole-document fail-closed assert is a strong backstop that catches leaks even where a complementary convention is missing. But the spine drops one genuinely load-bearing *mapping* (data-source → Module), and under-specifies two safety-relevant constructs (the `redacted` middle tier; the controlled-vocabulary constraint on free-text fields) that currently live only in the PRD prose, not in the spine's invariant layer.

---

## Coverage scorecard (the watch-items)

| Addendum element | Spine status | Assessment |
| --- | --- | --- |
| Three-tier privacy `public / redacted / aggregate_only` | `aggregate_only` + Allowlist fully in AD-4; `public`/`redacted` only via the `label` convention row; **`redacted` semantics not an invariant** | **Partial — F2 (medium)** |
| `config/*.yml` layout (identity/repos/redaction/exclusions/ai_sources) | All five present in Structural Seed + Conventions, **plus** `pricing.yml` (AD-11) | **Honored (exceeds)** |
| Code-exclusions list (`node_modules`, `.venv`, `dist`, …) | `exclusions.yml` exists; precise field set deferred to code; repo-count `exclusions` key fixed in PRD | **Deferred correctly** |
| Four Attribution Layers + v1.5 line-level path | AD-7 (MINOR bump, `attribution`), AD-9 (aggregate-only), Deferred (FR-13, git-notes) | **Honored** (layer detail = PRD/addendum) |
| Design-reference visual language | Absent from spine; AD-8 fixes render mechanism only | **Single-owner → correctly omitted; one data-shape note (F4, low)** |
| Data sources **per Module** | Three source *families* in AD-1 + Structural Seed; **no source→Module routing** | **Dropped mapping — F1 (high)** |
| "Do not invent token usage" honesty constraint | AD-11 (cost never estimated, omit-not-guess) + AD-10 (no token leaderboard) | **Honored (exceeds)** |

---

## Findings

### F1 — [high] The data-source → Module mapping is dropped; the spine's own Capability→Architecture Map stops short of the source axis

**What the addendum establishes (load-bearing).** The addendum's *"Consolidated v1 Module Scope, Data Sources & Invariants"* pins an explicit data source for each of the seven Modules:

1. Repo/metrics — GitHub GraphQL/REST (authed as `Pinstack`) **+ local clones**
2. Co-authorship — commit authors + `Co-authored-by:` trailers (git)
3. AI-native artefacts — filesystem detection of `CLAUDE.md`/`AGENTS.md`/`.cursorrules`/`.claude`/`mcp(.json)`
4. Agentic practice — local Claude Code **and** Codex logs (both)
5. Retrospective — **BMAD memlogs (planning) + git (coding)**
6. In-flight — live repo signals (WIP branches, open issues, draft PRs, TODO/FIXME, trajectory)
7. Redaction — reviewed config rules

**Where the spine falls short.** The spine carries the three source *families* (`AD-1`: "repo clones, agent logs, and BMAD memlogs"; Structural Seed: `~/Projects clones`, `~/.claude + ~/.codex logs`, `BMAD memlogs`) — but only as an undifferentiated bundle feeding `mods["7 Modules — filters"]`. There is **no routing**. The **Capability → Architecture Map** — the table whose entire job is to map each capability to where it lives and what governs it — has columns *Capability / FR*, *Lives in*, *Governed by*, but **no data-source column**. So the spine, read alone, does not fix:

- that **`retrospective.py` consumes BMAD memlogs + git** — and that "BMAD memlogs" is a source that exists for *this Module only* (non-obvious; easy to mis-wire into another Module or omit);
- that **`practice.py` requires *both* `~/.claude` and `~/.codex`** (a builder could wire one and silently under-count — degrading to a wrong figure, not a clean `available: false`);
- that repo/metrics is **GraphQL/REST + local clones** (two sources, not one).

**Why it clears the bar.** This is exactly the source→consumer wiring fact the spine claims to own ("calls a future builder … can't read off compliant code"). AD-3 makes each Module an independently-built unit owning one file; the source each unit reads is load-bearing per-unit knowledge, and divergence here (wrong source, missing second source) is silent and produces a *plausible-but-wrong* figure rather than a hard failure.

**Mitigant (why high, not critical).** The bound PRD fixes every source in §4 prose (FR-1 GitHub+clones; FR-5 local Claude Code+Codex logs; FR-11 BMAD memlogs+git; FR-12 live signals). The constraint *is* anchored in a companion the spine points to. The gap is that the spine's own map — the natural and stated home — omits the axis.

**Suggested fix (cheap).** Add one column to the Capability→Architecture Map: **"Data source."** Five rows are one token each; the two load-bearing ones are `BMAD memlogs + git` (retrospective) and `~/.claude + ~/.codex logs` (practice). Alternatively, label the Structural Seed edges (`memlogs → retrospective` only; `logs → practice` only) instead of fanning every source into the Module cloud.

---

### F2 — [medium] The `redacted` middle tier is under-specified: it lives only in the `label` convention row, not in the redaction invariant layer

**What the addendum establishes.** A **three-tier** privacy model — `public` (name + metrics), **`redacted` (generic description visible, no name)**, `aggregate_only` (metrics only) — with the middle tier carrying a distinct, load-bearing semantic: *the repo's existence and a generic description are shown, but every identifying string is suppressed.*

**Where the spine falls short.** The spine's redaction ADs (AD-4, AD-6) name **only** `aggregate_only` (the Silhouette default) and the Allowlist promotion. AD-4 says the Allowlist "promotes a repo above `aggregate_only`" but **never enumerates that the promotion targets are `public` *or* `redacted`**, and **never states the `redacted` invariant** (name suppressed; generic `category`/description shown; all other identifying strings still prohibited). The three-tier behaviour survives in the spine **only** in the Consistency-Conventions `label` row (`public`→label; non-public→generic `category`; `aggregate_only`→null/omitted) — i.e. as a *rendering* convention, not as a redaction *invariant*. The whole-document assert in AD-4 is written as if the world is binary (Silhouette vs allowlisted-open).

**Why it clears the bar.** The redaction gate (`redaction.py`) and a Module emitting a `redacted` repo are two independently-built units. If a repo is ever promoted to `redacted`, the gate must enforce "generic description OK, identifying strings still forbidden." That dual rule is a redaction invariant, and the spine's redaction ADs — the invariant home — don't carry it; a builder reading the redaction ADs alone would not know `redacted` is a tier the gate must handle distinctly from both `aggregate_only` and `public`.

**Mitigants (why medium).** (a) v1 ships with an **empty Allowlist**, so `redacted` is defined-but-unused in v1 — the gap cannot bite until a repo is promoted, which is a post-v1 event. (b) The PRD Glossary (*Display Tier*) and the PRD global-redaction contract fully define `redacted` semantics. (c) The `label` convention row does encode the rendering distinction. So the tier is representable and PRD-anchored; the gap is that the spine's *redaction invariant* is silent on it.

**Suggested fix.** In AD-4, change "promotes a repo above `aggregate_only`" to "promotes a repo to `redacted` (generic description, no identifying strings) or `public` (name + metrics)," and add one clause: a `redacted` repo's `label`/`category` is a generic description only and the whole-document assert still forbids every identifying string for it. One sentence closes it.

---

### F3 — [medium] The spine's redaction model is assert-only; the *generative* controlled-vocabulary constraint on free-text fields is not convention-ized

**What the addendum + bound PRD establish.** Redaction has two halves: a fail-closed **assert** over the whole document (AD-4 ✓), **and** a *construction-time* constraint that free-text-bearing fields are not free-typed. The PRD's global-redaction contract states it explicitly: *"Free-text-bearing blocks (`agentic_practice` confounders, `in_flight`, aggregate language/model labels) carry only aggregate integers/labels drawn from a **controlled vocabulary**."* This is where a novel client name would otherwise leak — `cost.confounders` and model/language labels are the soft spots.

**Where the spine falls short.** AD-4 names "`agentic_practice` incl. free-text confounders" as *in scope of the assert*, but the spine nowhere establishes the **controlled-vocabulary** convention for emitting those fields. The spine's redaction posture is therefore purely *detective* (assert + fail-closed), with no *preventive* convention. A builder reading the spine would emit free-typed confounders (e.g. a confounder string mentioning a client by name) and rely entirely on the assert's denylist to catch it.

**Why it clears the bar.** `practice.py` (writer of confounders) and `redaction.py` (validator) are independently built. If the writer free-types and the assert only checks against a denylist of *known* identifiers, a novel identifier passes — a real leak path. The controlled-vocabulary rule is what makes the two units agree by construction; it is load-bearing and currently lives only in PRD prose, not in the spine's conventions.

**Mitigants (why medium, not critical).** The AD-4 whole-document assert is a genuine backstop; the Consistency-Conventions row already says config drives redaction. The constraint is fully fixed in the bound PRD. The residual risk is the assert's coverage of *unknown* strings in free-text fields — exactly what a controlled vocabulary removes.

**Suggested fix.** Add to Consistency-Conventions (State & cross-cutting) one line: free-text-bearing JSON fields (`agentic_practice.cost.confounders`, language/model labels, `in_flight` labels) draw from a controlled vocabulary — never raw interpolation of repo/client-derived strings — so redaction is preventive as well as fail-closed.

---

### F4 — [low] The adopted visual language implies time-series the contract does not carry (heatmap + commits/month + LOC/month)

**What the addendum establishes.** The Design Reference (kept, not dropped, by the PRD's Aesthetic cluster) names specific adopted elements: a **GitHub-style daily-commit-intensity heatmap**, **commits/month** and **LOC/month** bar charts. The addendum's Dashboard Section 2 ("Activity over time — weekly/monthly: commits; active days; repos active; LOC touched") is the data behind them.

**Where it sits.** AD-8 fixes the *render mechanism* (build-time inline SVG, no charting library) — correct and sufficient for *how* charts are drawn. But the **data shape** those charts consume is not a load-bearing key anywhere: the v1 `build-ledger.json` (PRD §API Contracts) carries `in_flight.commit_trajectory` and `agentic_practice.cost.trend`, but **no per-day commit-intensity series and no per-month commits/LOC series**.

**Why only low, and why it is more an observation than a spine miss.** Aesthetic is **single-owner** (the one `site/` page) — there is no second unit to diverge with, so the visual language correctly stays out of an architecture spine and the PRD owns it. And the tension is **internal to the PRD**, not something the spine dropped: the PRD's Aesthetic cluster keeps the heatmap while the PRD's seven-Module scope omits an activity-over-time Module and §6.2 **defers momentum/decay windows to Vision**. So the contract not carrying a time-series is arguably *consistent with v1 scope* — but it leaves the kept heatmap/bar-charts without a data source. Logged as low because a builder wiring the page from the contract will find no series to render the adopted heatmap from.

**Suggested resolution (PRD-level, not spine).** Reconcile the PRD's Aesthetic cluster with its contract: either add an optional `activity_over_time` key (daily-intensity + monthly commits/LOC) — additive, MINOR-clean under AD-7 — or drop the heatmap/bar-charts from the v1 adopted visual language until momentum/decay lands. Architecture's only stake: if added, it is an additive optional key (AD-7), not a v1 load-bearing one.

---

## Deliberate overrides confirmed sound (not gaps — surfaced for traceability)

These are places the spine **departs from** the addendum (and in one case the PRD). The addendum is self-described as "starting proposals … not locked decisions," and each departure honors a *deeper* constraint, so none is a failure-to-honor. Surfaced so a downstream pass can reconcile the **PRD wording**, which still trails the spine.

- **Scheduler: GitHub Actions → local `launchd`/cron (AD-1, AD-12).** The addendum proposes *"scheduled GitHub Actions"* and the PRD still says *"weekly GitHub Action"* (FR-7, §6.1, Platform, Safety, NFRs). The spine **overrides both** to a local-only scheduler, on the load-bearing privacy ground that private client code, agent logs, and the auth token must never transit a third-party runner. This is the spine honoring the privacy invariant *over* the surface proposal — correct, and the stronger reading. **Action: reconcile the PRD's GitHub-Action language to the local scheduler**, or the PRD and spine will read in conflict to a builder.
- **Auth: "secret token in the Action" → local `gh`/env token only (AD-1, Conventions).** Direct consequence of the scheduler override; sound.
- **`pricing.yml` added to `config/` (AD-11).** Not in the addendum's five-file list; required by the "auditable cost or none" invariant. A justified addition, not a drift.

## Minor / sub-threshold (noted, not findings)

- **Exclusions taxonomy — "toy repos" and "abandoned experiments" dropped.** The addendum's discovery exclude/flag list includes *toy repos* and *abandoned experiments*; the structured `exclusions` key (spine + PRD identically) carries only `forks/vendored/generated/lockfiles/minified/bot_commits/mirrors`. Consistent across spine and PRD and properly deferred to `exclusions.yml`/config; the two dropped categories are subjective heuristics, reasonably not contract fields. Sub-threshold.
- **`diff_heuristic` "inferred, never merged into measured."** The addendum's Layer-4 honesty rule (label inferred; never fold into the measured figure) is fixed in PRD FR-13 + the `attribution` enum (`confidence: measured|inferred`), under the spine's deferred `attribution` representation (AD-7/AD-9). Correctly deferred with the v1.5 line-level path; not a v1 spine concern.
- **Methodology Note required contents (9 items).** Page content; defined in PRD Glossary + FR-9; not a cross-unit structural invariant. Correctly absent from the spine.
- **XLSX/PDF export + `pandas`/`openpyxl`.** Deferred (PRD §6.2); correctly absent from the spine Stack. The private CSVs and `methodology.md` are covered by AD-5's "raw evidence CSVs / per-client intermediates → drawer."

---

## Bottom line

The spine honors the addendum's load-bearing technical constraints well, and in several places **strengthens** them (local-only runtime over CI, `pricing.yml`, cost omit-not-guess, the whole-document fail-closed assert). The reconciliation gaps are:

- **F1 (high)** — the per-Module data-source mapping is dropped from the spine; its own Capability→Architecture Map is the natural home and lacks the axis (mitigated by PRD prose, but the spine claims this layer as its job). **Cheap fix: one table column.**
- **F2 (medium)** — the `redacted` middle tier is a rendering convention only, absent from the redaction invariant layer (dormant in v1 under the empty Allowlist; PRD-defined). **Fix: one clause in AD-4.**
- **F3 (medium)** — redaction is assert-only; the controlled-vocabulary constraint on free-text fields (the real leak path for novel client names) is not convention-ized in the spine (PRD-defined). **Fix: one line in Conventions.**
- **F4 (low)** — the adopted heatmap/bar-charts have no backing time-series in the contract; a PRD-internal tension to resolve, not a spine miss.

All four are spine-completeness improvements; none is a load-bearing constraint left unfixed across the spine **and** its bound PRD together. Hence **MINOR GAPS**, not REAL GAPS. The three one-line fixes (F1–F3) would close the substantive items entirely.
