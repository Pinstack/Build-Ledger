---
title: 'Brownfield Reconciliation Review — Spine ⇄ Spike'
artifact: ARCHITECTURE-SPINE.md (Build Ledger v1)
spike: collector/collect.py (v0.2) + public/build-ledger.json (current output)
reviewer: brownfield-reconciliation reviewer
date: '2026-06-25'
verdict: MINOR GAPS
---

# Reconciliation Review — does the Spine ratify & converge the Spike?

**Scope of this review.** Read the working spike (`collector/collect.py`, its current
`public/build-ledger.json` output) against the distilled `ARCHITECTURE-SPINE.md`. Report
(a) any good existing convention the spine silently drops or contradicts without reason, and
(b) any divergence the spine mischaracterizes, or any spike behavior that violates a spine AD
and isn't called out as a build punch-list item.

**One-line verdict: MINOR GAPS.** The spine's four-item punch-list is *accurate* but *not
complete*. The directional move (PRD shape authoritative; spike divergences are a build
punch-list, not new decisions) is correct and well-founded. But the spine misses several
convergence deltas that a future builder cannot read off the spine — most importantly the
fate of the spike's `commits_agent_authored` author-based signal (the misleading ~2.2%),
which AD-10 implicitly condemns but the punch-list never names, and the central-redaction /
private-drawer gap between AD-4/AD-5 and what the spike actually does.

---

## 1. The spine's punch-list characterization — confirmed item by item

Spine text (line 193):
> *The v0.2 spike (`collector/collect.py`) predates this contract; convergence deltas — string
> `schema_version` → semver `1.0.0`; `visibility` → `display_tier` + `allowlisted`; flat artefact
> list → the three Artefact Classes; exclusions list → counts — are a build punch-list, not new
> decisions.*

| # | Punch-list delta | Spike reality | Verified | Accurate? |
|---|---|---|---|---|
| 1 | string `schema_version` → semver `1.0.0` | `SCHEMA_VERSION = "build-ledger.v1"` (collect.py:25); output `"schema_version": "build-ledger.v1"` | ✅ | **Accurate.** AD-7 + Conventions table both demand `1.0.0`. Real delta, correctly scoped as a build task. |
| 2 | `visibility` → `display_tier` + `allowlisted` | `rec["visibility"] = "public"\|"private"` (collect.py:175); no `display_tier`, no `allowlisted` key anywhere in output (verified: both absent) | ✅ | **Accurate.** AD-4 makes `display_tier: aggregate_only` the default and `allowlisted: false` an explicit per-repo field; Conventions table keys `label` off `display_tier: public`. Real delta. |
| 3 | flat artefact list → three Artefact Classes | `signals.ai_artefacts` is a flat `["CLAUDE.md","AGENTS.md",...]` list (collect.py:127–136); lives *inside* `signals`, not as its own `ai_artefacts` top-level/section | ✅ | **Accurate but understated** — see Finding B. The class restructure is real; the spine also relocates this from `signals.ai_artefacts` to `repositories[].ai_artefacts` (Capability Map line 184), a move the prose delta doesn't mention. |
| 4 | exclusions list → counts | `EXCLUSIONS = [...]` list of 6 strings (collect.py:32); output `"exclusions": [...]` flat string list | ✅ | **Accurate.** The contract wants exclusion **counts** (how many forks/vendored/lockfiles excluded), not a static prose list. Real delta. Note: `exclusions` is not owned by any of the 7 Modules in the Capability Map — see Finding E. |

**Conclusion on §1:** all four named deltas are genuine spike→contract divergences, none is a
mischaracterization, and treating them as a build punch-list (not re-litigated decisions) is the
right call. The spike's own header comment already anticipates the contract direction (silhouettes,
allowlist-empty, lower-bound hero), so ratification is sound. **The characterization is accurate;
it is the *completeness* that has gaps (§3).**

---

## 2. Targeted checks requested

### 2a. Central redaction + hard assert vs AD-4 / AD-5 — PARTIAL MATCH

**What AD-4/AD-5 require:** a *single* redaction pass over the **entire** document
(`repositories[]`, `aggregates`, `agentic_practice` incl. free-text, `retrospective.window_view`,
`in_flight`), **fail-closed**, living in a dedicated central gate `collector/redaction.py`; and
private outputs (`mirror.json`, raw CSVs) written **outside** the source tree.

**What the spike does (collect.py:193–198):**
```python
# ---- SAFETY GATE: no private record may carry identifying fields ----
for rec in out_repos:
    if rec["visibility"] == "private":
        assert not ({"name","repo"} & rec.keys()), "REDACTION LEAK: ..."
        co = rec.get("coauthorship") or {}
        assert "ai_models" not in co, "REDACTION LEAK: ..."
```

- ✅ **Fail-closed via hard `assert`** — matches AD-4's "the run does not publish" intent. Good
  existing convention; the spine *should* explicitly ratify the `assert`-before-write idiom (it
  describes the behavior but never blesses the spike's mechanism).
- ✅ **Safe-by-default silhouette** — every private repo is redacted by default; `ALLOWLIST` empty,
  so every private repo stays a silhouette (collect.py:27, 157, 182). Matches AD-4. Verified in
  output: 0 private records carry `name`/`repo`; 0 carry `ai_models`.
- ⚠️ **NOT whole-document, NOT a central module.** The assert loops over `out_repos` **only**. It
  does **not** scan `aggregates`, `agentic_practice`, `retrospective`, `in_flight`, or
  free-text/`note` fields. AD-4 explicitly names all of these as in-scope for the single pass. In
  v0.2 those sections are stubbed (`available:false`), so nothing leaks *today* — but the assert is
  structurally narrower than AD-4 mandates. **This is a punch-list item the spine does NOT call out**
  (Finding A). The redaction is also inlined in `main()`, not the `collector/redaction.py` central
  gate the source tree (lines 165, 188) and AD-4 prescribe.
- ⚠️ **Assert is allow-by-omission, not assert-by-enumeration.** The spike asserts only that two
  known-bad keys (`name`/`repo`, `ai_models`) are absent. AD-4's model is the inverse — assert the
  *entire* document is clean of *all* prohibited fields (paths, branches, commit messages, client
  names, secrets, transcripts). A future `branch`/`path` field added to a silhouette would sail
  through the current gate. The spine's "whole-document assert" wording is the correct convergence
  target; the spike is a narrower precursor. Correctly *implied* by AD-4 but not flagged as a delta.

**Verdict 2a:** the spike's fail-closed assert is the right *spirit* and AD-4 ratifies it, but the
spike is **partial** against AD-4 (per-record, not whole-doc; inline, not central). The spine
does not list "centralize + widen the redaction pass to whole-document" as a punch-list item — it
should. See Finding A.

### 2b. Does the spike write private output INTO the repo tree? — NO PRIVATE OUTPUT YET, but the one output IS in-tree

- The spike's **only** write is `OUT = .../public/build-ledger.json` (collect.py:24, 233–234),
  which is the **public, post-redaction** artifact. That is *correct* per AD-5 (the single
  private→public crossing). `public/` is confirmed inside the project tree.
- The spike writes **no** `mirror.json`, **no** raw CSVs, **no** per-client intermediates — it has
  **no private-output path at all** (no `~/.build-ledger/`, no drawer, grep-confirmed). So the
  literal AD-5 violation ("private output into the tree") **does not occur** — because the spike
  doesn't yet produce the private artifacts AD-5 governs (mirror view, raw evidence). The
  retrospective mirror_view (AD-6), agentic-practice raw logs, and per-client CSVs are all
  unbuilt (`available:false`).
- ⚠️ **Forward gap:** when those Modules land, AD-5 requires their private outputs to go to
  `~/.build-ledger/private/` (outside the tree). The spike establishes **no** such drawer
  convention — `OUT` is the only output path and it's in-tree. A builder extending the spike in
  place would naturally drop a `mirror.json` next to `build-ledger.json` (in `public/` or
  `collector/`), which AD-5 forbids. The spine *states* the drawer rule but the spike provides **no
  scaffolding** for it; this is a "establish the private drawer path" punch-list item the spine
  omits. See Finding C.

**Verdict 2b:** **No in-tree private leak today** (the spike's sole output is the public artifact,
correctly placed). But the spike has **zero** private-drawer machinery, and AD-5/AD-6's
out-of-tree requirement is therefore **entirely unbuilt** — not flagged as a build task.

### 2c. Does the spike read clones from ~/Projects? — YES, matches AD-5

- `PROJECTS_DIR = Path.home() / "Projects"` (collect.py:23), iterated read-only in
  `local_clone_map()` (collect.py:61–72). ✅ **Matches AD-5** exactly ("reads clones from
  `~/Projects`"). Good existing convention, correctly ratified by AD-5. No gap.
- Note (not a gap): the spike auto-discovers clones by walking `~/Projects` and matching `origin`
  remotes, rather than reading a reviewed `config/repos.yml`. AD-1/AD-5 ratify reading from
  `~/Projects`; the *config-driven* repo list (Conventions "Config" row; source tree `repos.yml`)
  is a convergence the spine implies but the spike does by filesystem walk. Minor — listed in
  Finding E as a config-externalization delta.

### 2d. The `commits_agent_authored` author-based secondary signal (the misleading ~2.2%) — UNHANDLED by the spine

This is the **most important finding** and the one the user explicitly asked about.

**The spike computes two signals (collect.py:75–121):**
1. **Trailer-based (HERO):** commits carrying `Co-authored-by: <AI model>` →
   `commits_ai_coauthored` (1277, 61.4% of 2080). This is what AD-10 sanctions as the lower-bound
   hero (`unit: "commit"`).
2. **Author-based (secondary):** commits an agent *identity* authored autonomously →
   `commits_agent_authored`. Verified value: **46 / 2080 = 2.21%** (the "misleading 2.3%").

The spike **surfaces #2 prominently**: it's in per-repo `coauthorship` (collect.py:114),
**survives into private silhouettes** (it's not stripped — only `ai_models` is, collect.py:189),
sits in top-level `aggregates.commits_agent_authored` (collect.py:217), **and is printed to the
audit stdout** as "agent-authored (autonomous)" (collect.py:240).

**Why it's misleading (and why AD-10 implicitly condemns it):** 2.2% looks like "AI wrote 2% of
the work," which *understates* AI-native involvement by ~28× versus the 61.4% co-authored reality.
It's exactly the kind of figure that misrepresents the provenance story. AD-10 mandates the
commit-level co-authored share be "rendered as an explicit **lower bound** … never as the total"
— but says **nothing** about the author-based autonomous count, which is a *different*, lower, more
misleading number sitting right beside it.

**The gap:** the spine/contract does **not** decide the fate of `commits_agent_authored`. It is:
- **NOT kept** — no contract key for it; not in the Capability Map; not named in any AD.
- **NOT dropped** — no AD or punch-list item says "remove the author-based autonomous count."
- **NOT mapped** — not reconciled to any v1 contract field or relabeled.

It simply **falls through the cracks**. A builder converging the spike to the contract has no
instruction on whether to carry `commits_agent_authored` forward, suppress it, or demote it to a
non-headline raw signal. Given AD-10's anti-vanity / anti-misleading stance and AD-3's
"each Module owns exactly one key," the *intended* answer is almost certainly **drop it from the
public headline (and at minimum never let it read as a total)** — but the spine must **say so**.
Leaving a 2.2% "agent-authored" figure in `aggregates` and on stdout, unaddressed, is precisely
the provenance-misrepresentation AD-10 exists to prevent. **This is a REAL convergence gap the
spine missed** (Finding D, the headline finding).

(Sub-note: the stdout `print` of "agent-authored (autonomous)" is fine re: AD-4 logging — it's an
aggregate count, no repo names — but it propagates the misleading framing into the operator's eye.)

---

## 3. Findings (good conventions dropped / divergences mischaracterized / uncalled punch-list)

### Finding A — [high] Redaction pass is per-record, not whole-document; and inline, not central — not on the punch-list
AD-4 mandates a **single whole-document** assert (over `aggregates`, `agentic_practice` free-text,
`retrospective.window_view`, `in_flight`, as well as `repositories[]`) in a dedicated
`collector/redaction.py`. The spike asserts only over `out_repos`, only for two known-bad keys,
inline in `main()` (collect.py:193–198). The spine ratifies the *behavior* (fail-closed assert) —
good — but does **not** list "extract to central gate + widen to whole-document + assert-by-
enumeration of prohibited fields" as a build task. A future builder reading the punch-list would
think redaction is essentially done. It is not. **Add to punch-list.**

### Finding B — [medium] The artefact restructure also *relocates* the key (`signals.ai_artefacts` → `repositories[].ai_artefacts`) — under-described
The punch-list says "flat artefact list → three Artefact Classes." True, but incomplete: the spike
nests artefacts inside `signals` (collect.py:128–134), while the contract (Capability Map line 184)
gives `ai_artefacts` its own home on the repo record, owned by `modules/artefacts.py` (a *separate*
Module from whatever owns `signals`). So the delta is **two** changes: (1) flat list → 3 classes,
(2) relocate out of `signals` into a Module-owned `ai_artefacts` key (AD-3 one-key-per-Module). Also
note: the spike has **no `signals` Module** in the 7-Module decomposition at all — `has_tests`,
`has_ci`, `has_migrations`, `tracked_files` etc. (collect.py:124–136) are real, useful signals the
spike emits but the spine's Module map never accounts for. Where do they land? Presumably
`modules/repos.py` (the repo-metrics Module), but the spine never says. **Convergence gap: map the
spike's `signals` block to a Module/key.**

### Finding C — [medium] No private-drawer scaffolding; AD-5/AD-6 out-of-tree outputs entirely unbuilt and unflagged
The spike has exactly one output path (`OUT`, in-tree, public). AD-5's `~/.build-ledger/private/`
drawer and AD-6's private `mirror.json` have **no** precursor in the spike — not even a stub path
constant. The natural way to extend the spike (write `mirror.json` beside `build-ledger.json`)
**violates AD-5**. The spine states the rule but provides no "establish the drawer + route private
outputs there" punch-list item. Low blast radius today (nothing private is written yet), but it's a
landmine for the builder. **Add to punch-list.**

### Finding D — [high] `commits_agent_authored` (the misleading ~2.2%) is neither kept, dropped, nor mapped — the spine's biggest omission
See §2d in full. The spike surfaces a 2.2% author-based "agent-authored" figure in per-repo
records, **private silhouettes**, top-level `aggregates`, and stdout. AD-10 polices the *hero*
co-authored share as a lower bound but is silent on this lower, more-misleading sibling. The
contract has no field for it and no AD drops it. **The spine must explicitly decide its fate**
(recommended: drop from public aggregates/headline per AD-10's anti-misleading mandate, or demote
to a clearly-labelled raw inspectable signal that can never read as "% of work AI did"). As written,
the convergence is **undecided**, which is worse than either keeping or dropping it. This is the
finding most worth surfacing.

### Finding E — [low] `exclusions` and config-externalization are orphaned in the Module map
Two small structural orphans:
- The contract's `exclusions` (→ counts, per punch-list #4) is a top-level key but is owned by
  **none** of the 7 Modules in the Capability Map (lines 182–191). AD-3 says every top-level key has
  exactly one owning Module. Who writes `exclusions`? Unspecified. Likely `collect.py` itself or
  `repos.py`, but the spine doesn't say.
- The spike hard-codes `EXCLUSIONS`, `AI_AGENT`/`BOT` regexes, `GITHUB_ACCOUNT`, and discovers repos
  by filesystem walk (collect.py:22–33, 61–72). The Conventions "Config" row + source tree
  (`config/*.yml`) require these to be **reviewable config** (`identity.yml`, `repos.yml`,
  `ai_sources.yml`, `exclusions.yml`). This config-externalization is a genuine spike→contract
  delta the punch-list **omits** — and it's load-bearing for FR-6 ("reviewed before any private
  clone"). The classifier regexes especially must become reviewable `ai_sources.yml`. **Add to
  punch-list.**

### Finding F — [low] `available:false` stubs use `note`, not AD-3's "empty sub-objects"
AD-3: "A Module with no data this run emits `available: false` with **empty sub-objects** — never
silent omission." The spike's stubs (`agentic_practice`, `retrospective`, `in_flight`,
collect.py:227–229) emit `{"available": false, "note": "..."}` — `available:false` ✅ but a `note`
string rather than empty sub-objects. Trivial, but a convergence nuance: the contract shape for an
unavailable Module should be settled (is `note` allowed? are empty sub-objects required?). Minor.

### Finding G — [informational, not a gap] Good spike conventions the spine *correctly* ratifies
For balance — these are existing conventions the spine **keeps**, correctly:
- Reading clones read-only from `~/Projects` (AD-5) ✅
- Fail-closed `assert`-before-write (AD-4) ✅
- Safe-by-default silhouette; allowlist empty in v1; allowlist as the *only* promotion mechanism
  (AD-4) ✅ — spike header comment and code (collect.py:27, 182) match AD-4 verbatim in spirit.
- Hero = co-authored split as explicit lower bound (`unit:"commit"`), bot noise classified out of
  the headline (AD-10) ✅ — spike `BOT` regex + `commits_bot_excluded` (collect.py:30, 218) match.
- Bot-authored commits excluded from the headline (AD-10, exclusions) ✅
- One immutable file per run, written fresh (AD-2/State convention) ✅
- Aggregate-only stdout audit, no repo names/paths (AD-4 Logging) ✅ — collect.py:237–245 prints
  counts only.
None of these are dropped or contradicted. The ratification of the spike's *safety posture* is
faithful and is the spine's strongest section.

---

## 4. Bottom line

**The spine correctly RATIFIES the spike's safety posture and CONVERGES its shape divergences —
but the convergence is incomplete.** The four named punch-list deltas are all real and accurately
characterized (no mischaracterizations found). The directional judgment — PRD shape authoritative,
spike deltas are build tasks not new decisions — is sound and well-supported by the spike's own
forward-looking header.

**What the spine missed (the completeness gaps):**
1. **[high] `commits_agent_authored` ~2.2%** — undecided fate (neither kept/dropped/mapped);
   AD-10 implicitly condemns it but no AD/punch-list names it. *The headline gap.* (Finding D)
2. **[high] Redaction not whole-document / not centralized** — spike's assert is per-record + inline;
   AD-4 wants whole-doc + `redaction.py`. Not on the punch-list. (Finding A)
3. **[medium] Artefact key relocation + the orphaned `signals` block** — the restructure is bigger
   than "flat→3 classes"; the spike's `signals` metrics map to no named Module. (Finding B)
4. **[medium] No private-drawer scaffolding** — AD-5/AD-6 out-of-tree outputs unbuilt and unflagged;
   extending the spike in place would violate AD-5. (Finding C)
5. **[low] Config-externalization + `exclusions` ownership** orphaned in the Module map. (Finding E)

**No critical defects** (no actual private-data leak; the in-tree output is the correct public
artifact; ~/Projects read matches AD-5; fail-closed assert present). Hence **MINOR GAPS**, not REAL
GAPS — but Findings A and D should be promoted into the spine's punch-list (or an AD note) before a
builder treats the spike as "just needs the four renames."
