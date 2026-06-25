---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories", "step-04-final-validation"]
inputDocuments:
  - _bmad-output/specs/spec-build-ledger/SPEC.md
  - _bmad-output/planning-artifacts/prds/prd-Build-Ledger-2026-06-24/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-Build-Ledger-2026-06-25/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/briefs/brief-Build-Ledger-2026-06-24/addendum.md
---

# Build Ledger - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Build Ledger, decomposing the requirements from the SPEC (canonical contract), the PRD, and the Architecture spine into implementable stories. **Brownfield:** a working v0.2 collector spike (`collector/collect.py`) exists; its convergence to the locked contract is real early work, not a from-scratch build.

## Requirements Inventory

### Functional Requirements

```
FR-1:  Collector discovers Pinstack repositories and computes conventional metrics (counts, commits, active days, LOC, languages, test/CI/migration presence) from source, applying the Excluded-from-counts list before any figure. [CAP-1]
FR-2:  Generated Page renders conventional metrics subordinate to provenance — hero leads with Co-Authorship Split / AI-Native Artefacts; raw LOC is never the first or largest figure. [CAP-1]
FR-3:  Collector derives the commit-level Co-Authorship Split per repository (human + named agent authors from commit authors + Co-authored-by trailers), presented as an explicit lower bound. [CAP-2, HERO]
FR-4:  Collector detects AI-Native Artefacts (CLAUDE.md/AGENTS.md/.cursorrules/.claude/mcp) and classifies each into exactly one of three Artefact Classes. [CAP-3]
FR-5:  Collector computes aggregate agentic practice/efficiency (cadence, model mix, cache-hit ratio, cost totals, cost trend) from local Claude Code + Codex logs without reading or emitting transcript content. [CAP-4]
FR-6:  Collector enforces the Redaction Rules on every run — every private repo defaults to display_tier aggregate_only; a whole-document assert runs before publish; fail-closed; Allowlist (empty v1) is the only promotion path. [CAP-7, SAFETY-CRITICAL]
FR-7:  Collector runs weekly via a local scheduler (launchd/cron) and manually on demand; one manual run produces a publishable cut (fast-track). [CAP-9]
FR-8:  Collector emits exactly one build-ledger.json per run conforming to the documented shape, carrying schema_version, every Module nested, a no-data Module represented as available:false. [CAP-8]
FR-9:  Generated Page renders at the Route with visible Ledger Metadata, the Methodology Note, and the Excluded-from-counts Note. [CAP-10]
FR-10: Generated Page survives skeptical inspection — no fabricated figure, no leak, no runtime break on latest desktop Chrome/Safari/Firefox. [CAP-11]
FR-11: Collector produces a sourced Retrospective in two framings — a curated Window View that publishes, a brutally-honest Mirror View that is private-only. [CAP-5]
FR-12: Collector renders In-Flight from auditable live repo signals only (WIP branches, open issues, draft PRs, in-code work-markers, commit trajectory) — never aspirational. [CAP-6]
FR-13: [v1.5 — OUT OF v1 SCOPE] Recover Line-level Attribution from local Claude Code/Codex session logs (session-diff reconciliation), backfilled, aggregate-only. Lands via the optional `attribution` representation under a schema MINOR bump. Tracked, not built in v1.
```

### NonFunctional Requirements

```
NFR-1 (Auditability):   Every published figure is reconcilable from source or the Methodology Note — "inspectable or it doesn't ship" is a release gate.
NFR-2 (Reproducibility): A given build-ledger.json fully determines the page; re-rendering the same file yields the same page.
NFR-3 (Determinism of exclusions): The Excluded-from-counts Note reflects exactly what the Collector excluded on that run.
NFR-4 (Freshness/observability): Ledger Metadata (run timestamp, collector version, schema_version) is visible on every run so staleness is self-evident.
NFR-5 (Performance): The weekly local run completes in a few minutes; the static page loads fast on a current desktop browser.
NFR-6 (Contract portability): build-ledger.json is the stable boundary; collector internals (LOC tool, language detection) may change without changing the page provided the schema holds.
NFR-7 (Security): Secrets never transit the public surface; the Pinstack token is local-only (gh/env); publication is fail-closed.
NFR-8 (Cost): $0 operational — static page + weekly local run, no backend, no paid CI; efficiency-as-craft only, no invented economics.
NFR-9 (Privacy — SAFETY-CRITICAL): No private repo name/path/branch/commit-message/secret/client-name/transcript ever leaks; Redaction Rules reviewed before any private clone (~35 real client repos).
```

### Additional Requirements

*Architecture spine (ARCHITECTURE-SPINE.md) — the 15 binding ADs as technical requirements. Stories cite AD ids.*

```
STACK / STARTER:
- Collector: Python 3.14 (BROWNFIELD — v0.2 spike collect.py exists; converge it, don't rebuild). Tools: gh CLI, git, tokei.
- Site: Astro 6 (GREENFIELD — scaffold a minimal Astro shell + the /engineering page). Node 24 LTS. → Epic 1 / page epic Story 1 = scaffold.
- Deploy: wrangler → Cloudflare Pages free tier (host swappable), pre-built local deploy, $0.
- Repo topology: ONE public repo (collector + site + published build-ledger.json); private outputs written OUTSIDE the repo tree (~/.build-ledger/private/).

ARCHITECTURE DECISIONS (binding):
- AD-1  Local-primary runtime — collector runs only on a trusted local machine; sole producer; never CI for collection.
- AD-2  Single versioned contract — build-ledger.json is the only coupling; page renders solely from it.
- AD-3  Module ownership — each Module owns one slice; assembler is sole file writer; no-data = available:false (typed-empty).
- AD-4  Fail-closed whole-document redaction — assert over the entire public doc before publish; controlled-vocabulary free-text; 3-value display_tier enum; empty Allowlist.
- AD-5  Private outputs outside the repo tree — repo cannot contain private data by construction.
- AD-6  Mirror View never public — public retrospective carries window_view only; no mirror_view key.
- AD-7  Semantic versioning — semver; additive=MINOR (forward-compat attribution rep); breaking=MAJOR the page refuses.
- AD-8  Build-time static render — static HTML/CSS/SVG from the file; charts are server-generated inline SVG; islands only where interactive.
- AD-9  Aggregate-only, no raw transcripts — log-derived modules emit counts/ratios only.
- AD-10 Provenance-first, anti-vanity contract — no spend-leaderboard/Wrapped/counter structure; commit-share a labelled lower bound.
- AD-11 Auditable cost or none — pinned/dated/labelled price table (config/pricing.yml) or logged figures; never estimated; omit if unsourceable.
- AD-12 Pre-built local deploy to a free static host — no host build, no Actions, $0.
- AD-13 Assembler owns shared collections — collect.py owns repositories[] + ids; Modules contribute id-keyed maps.
- AD-14 Aggregates are a derived projection — pure function of the emitted rows; reconcilable by construction.
- AD-15 One atomic, deterministic, fail-closed run — build in memory → atomic replace; tiering→aggregate→assert→write.

CONFIG (reviewable, addendum): config/{identity,repos,redaction,exclusions,ai_sources,pricing}.yml.
SPIKE CONVERGENCE PUNCH-LIST: string schema_version→semver 1.0.0; visibility→display_tier+allowlisted; flat artefacts→3 classes; exclusions list→counts; drop author-based commits_agent_authored; lift inline redaction→central redaction.py whole-doc assert; split assembly→assembler; scaffold the out-of-tree private drawer.
```

### UX Design Requirements

*No formal bmad-ux contract exists; these are lifted from the PRD's Aesthetic & Tone (lightweight — v1 page is minimal-but-clean, the collector is the bulk of the work).*

```
UX-DR1: Restrained, numerical, auditable light theme — monospace caps labels, large clean numerals, muted accent, GitHub-style commit-intensity heatmap, commits/month + LOC/month bar charts (server-generated inline SVG), card-grid layout.
UX-DR2: Provenance-first hero — the Co-Authorship Split + AI-Native Artefacts lead; repos/commits/LOC demoted to supporting cast.
UX-DR3: Honest-floor framing — render the commit-level AI-co-authored share (~61.4%) as an explicit lower bound ("≥ … of commits, commit-level"); never round up to the line-level story before v1.5.
UX-DR4: Anti-"AI wizard" voice — measured superlatives ("largest measured codebase"); the framing line near the top: "This is not a productivity score. It is an evidence ledger…".
UX-DR5: Integrity cues kept, theatre dropped — generated-from-source signal, Methodology Note, Excluded-from-counts Note; NO "SAMPLE DATA" banner, NO per-figure trust badges (cut).
UX-DR6: Drill-to-evidence — every headline figure is one interaction (link/expand) from its underlying evidence or the Methodology explanation.
```

### FR Coverage Map

```
FR-1  → Epic 1  (repo metrics from source, into repositories[])
FR-2  → Epic 3  (volume subordinate to provenance on the page)
FR-3  → Epic 2  (commit-level Co-Authorship Split — HERO)
FR-4  → Epic 2  (AI-Native Artefact detection + 3-class classification)
FR-5  → Epic 4  (aggregate agentic practice, no transcripts)
FR-6  → Epic 1  (fail-closed whole-document redaction — SAFETY-CRITICAL)
FR-7  → Epic 3  (local schedule + on-demand fast-track + deploy)
FR-8  → Epic 1  (single build-ledger.json contract + assembler)
FR-9  → Epic 3  (Generated Page + Ledger Metadata + Methodology)
FR-10 → Epic 3  (survives skeptical inspection as a work sample)
FR-11 → Epic 4  (two-framing Retrospective; mirror private)
FR-12 → Epic 4  (In-Flight from auditable signals only)
FR-13 → v1.5    (Line-level Attribution — OUT OF v1 SCOPE; non-breaking MINOR later)
```

## Epic List

### Epic 1: A redaction-safe evidence file from real repositories
Running the Collector once produces a schema-valid, fully-redacted `build-ledger.json` computed from the subject's real repositories — with the client-privacy guarantee **proven before anything is ever published**. This is the auditable artifact every later epic emits into, and the safety floor that makes publishing OK at all. Delivers the contract + assembler + atomic fail-closed run, the central redaction system + out-of-tree private drawer, base repo metrics, and the v0.2 spike's convergence to the locked contract.
**FRs covered:** FR-1, FR-6, FR-8 — ADs AD-1/2/3/4/5/13/14/15.

### Epic 2: Provable agentic authorship (the hero)
The decisive provenance evidence lands in the file — the commit-level **Co-Authorship Split** (named human + agent authors, stated as an explicit lower bound) and the classified **AI-Native Artefacts** — redaction-safe, inspectable, computed from source. This is the evidence the Window grades first; it builds on Epic 1's `repositories[]` rows and redaction.
**FRs covered:** FR-3, FR-4 — ADs AD-7/9/10.

### Epic 3: A published, inspectable page that backs the DM (fast-track)
A live static page at `raedmund.com/engineering`, rendered from the file and deployed pre-built from local — provenance-first, with Ledger Metadata, the Methodology Note, and the Excluded-from-counts Note — that survives a skeptic's "fragile or flawed?" read. **One manual run produces this publishable cut (the fast-track that backs the GL DM)**; the weekly local schedule then keeps it fresh. The quieter Mirror sections render as "no data this run" until Epic 4 fills them (module-availability contract).
**FRs covered:** FR-2, FR-7, FR-9, FR-10 — UX-DR1…6, ADs AD-8/11/12.

### Epic 4: The Mirror — honest self-insight signals
The builder gets a true read on his own trajectory: **Agentic Practice & Efficiency** (aggregate, efficiency-as-craft), the two-framing **Retrospective** (curated Window View publishes; brutally-honest Mirror View stays private in the out-of-tree drawer), and auditable **In-Flight**. These light up the page's quieter sections without touching the Window-facing hero path — co-equal value (the Mirror), sequenced after the DM milestone.
**FRs covered:** FR-5, FR-11, FR-12 — ADs AD-6/9/11.

*Out of v1: FR-13 (Line-level Attribution + Acceptance Ratio) — v1.5, lands via a non-breaking schema MINOR bump; tracked, not built here.*

---

## Epic 1: A redaction-safe evidence file from real repositories

A schema-valid, fully-redacted `build-ledger.json` from real repositories, with client-privacy proven before anything publishes — the foundation every later epic emits into.
**FRs:** FR-1, FR-6, FR-8 · **ADs:** AD-1/2/3/4/5/13/14/15

### Story 1.1: Project skeleton with an out-of-tree private drawer

As the builder,
I want one public repo plus a private output location outside the repo tree and a reviewable config scaffold,
So that private data physically cannot enter anything publishable, by construction.

**Acceptance Criteria:**

**Given** the project layout, **When** the repo is initialized, **Then** it contains `collector/`, `site/`, and a `.gitignore` ignoring any in-tree `private/`, **And** the Collector's private outputs are configured to write to a path outside the repo tree (e.g. `~/.build-ledger/private/`). *(AD-5)*

**Given** the config scaffold, **When** created, **Then** `config/{identity,repos,redaction,exclusions,ai_sources,pricing}.yml` exist as reviewable files, **And** `repos.yml`/`redaction.yml` are reviewed before any private clone is read. *(FR-6)*

**Given** a deliberate attempt to write a private artifact, **When** the Collector runs, **Then** the private file lands outside the repo tree **And** `git status` shows nothing private staged.

### Story 1.2: The build-ledger.json contract + schema versioning + validator

As the builder,
I want a documented `build-ledger.json` shape with a semver `schema_version` and a validator,
So that the Collector and the page have one stable contract to build against.

**Acceptance Criteria:**

**Given** the documented top-level shape, **When** a file is emitted, **Then** it carries `schema_version: "1.0.0"` at top level and in `ledger_metadata`, **And** the two are equal. *(AD-2, AD-7)*

**Given** a Module with no data, **When** the file is assembled, **Then** that Module's key is present as `available: false` with a typed-empty sub-object, never omitted. *(AD-3)*

**Given** any candidate file, **When** the validator runs, **Then** a file matching the documented shape passes and a malformed one fails with a clear error.

### Story 1.3: The assembler — discovery, stable ids, tiering, id-keyed merge

As the builder,
I want a run that discovers repos, assigns each a stable id and display_tier, and merges each Module's contribution by id,
So that the file is assembled by one owner with no two Modules fighting over the same array.

**Acceptance Criteria:**

**Given** repository discovery as Pinstack, **When** the run starts, **Then** every repo gets a stable opaque `id` owned by the assembler **And** each private repo is tiered `display_tier: aggregate_only` (tiering is the first pipeline stage). *(AD-13, AD-1)*

**Given** per-repo Modules, **When** they contribute, **Then** each returns an id-keyed map for its own field-path and the assembler merges by id (no Module writes the array). *(AD-13)*

**Given** a degraded Module (no/failed data), **When** the run proceeds, **Then** that Module is set `available:false` and the run continues. *(AD-3)*

*(Convergence: absorbs the spike's array/aggregate assembly currently inline in `main()`.)*

### Story 1.4: Central fail-closed redaction + atomic publish

As the builder,
I want a single redaction pass that asserts over the entire public document and then writes it atomically,
So that no private data can reach the public surface, an unsafe run does not publish, and a run never leaves a torn file.

**Acceptance Criteria:**

**Given** the assembled document, **When** redaction runs, **Then** it asserts over the WHOLE document (repositories[], aggregates, agentic_practice incl. free-text confounders, retrospective.window_view, in_flight) that none of the prohibited fields appear (name/path/branch/commit-message/secret/client-name/transcript). *(FR-6, AD-4)*

**Given** a private repo, **When** emitted, **Then** it is a Silhouette (`display_tier: aggregate_only`, no `label`, metrics/signals/aggregate counts only) **And** the Allowlist is empty so every `allowlisted` is `false`. *(AD-4)*

**Given** free-text-bearing fields, **When** populated, **Then** they carry only controlled-vocabulary labels / aggregate integers (allowlist by construction), not arbitrary scanned text. *(AD-4)*

**Given** a fixture with a synthetic private repo exercising all five public blocks, **When** published, **Then** the file contains none of the prohibited fields and has no `retrospective.mirror_view` key. *(FR-6, AD-6)*

**Given** the redaction assert passes, **When** the file is published, **Then** the in-memory document is written by atomic replace (temp + rename); **And** if the assert fails the publish aborts, leaving the previous file intact (fail-closed). *(AD-15, AD-4)*

**Given** the same inputs, **When** the run repeats, **Then** the output is byte-stable except for genuinely changed data (deterministic ordering, so the committed diff reflects real change). *(AD-15)*

*(Convergence: lifts the spike's inline per-record redaction into the central `redaction.py` whole-document assert.)*

### Story 1.5: Base repo metrics + signals + derived aggregates with exclusions

As Dana (the evaluator),
I want conventional metrics computed from source with exclusions applied,
So that every figure is real and bounded, not padded.

**Acceptance Criteria:**

**Given** the repos, **When** metrics compute, **Then** `repositories[].metrics` (commits, active_days, files, loc_added/removed/net) and `.signals` (has_tests/has_ci/has_migrations) are computed from source. *(FR-1)*

**Given** the Excluded-from-counts list, **When** metrics compute, **Then** forks/mirrors/vendored/generated/lockfiles/minified/bot-commits are excluded before any figure **And** the exclusion counts are recorded in `exclusions`. *(FR-1)*

**Given** the emitted rows, **When** aggregates compute, **Then** `aggregates` is a pure derived projection of `repositories[]` **And** each total equals the sum of the rows it summarizes. *(AD-14)*

### Story 1.6: End-to-end verification over all real repositories

As the builder,
I want a full run over the real repositories proven to emit the locked contract with a clean leak-scan,
So that the incrementally-converged collector is verified contract-true on real data, not just in unit tests.

*(The spike's punch-list — semver `schema_version`, `display_tier`+`allowlisted`, exclusions-as-counts, author-based `commits_agent_authored` dropped, inline redaction lifted, assembly split — is absorbed incrementally across Stories 1.2–1.5 as each slice is built; this story proves the whole.)*

**Acceptance Criteria:**

**Given** the converged collector, **When** a full run executes over all real repositories, **Then** it emits a schema-valid `build-ledger.json` (public named, private silhouettes) with no legacy spike fields (`visibility`, flat artefact list, string schema_version, author-based signal) remaining. *(FR-8, AD-2)*

**Given** that run, **When** the whole-document redaction assert executes, **Then** the leak-scan is clean (no prohibited fields anywhere, no `mirror_view` key) and the run is fail-closed. *(FR-6)*

**Given** aggregates vs rows, **When** verified, **Then** every headline total reconciles with the sum of the repository rows it summarizes. *(AD-14)*

---

## Epic 2: Provable agentic authorship (the hero)

The decisive provenance evidence — the commit-level Co-Authorship Split and the classified AI-Native Artefacts — redaction-safe and computed from source.
**FRs:** FR-3, FR-4 · **ADs:** AD-7/9/10

### Story 2.1: Commit-level Co-Authorship Split per repository (the hero)

As Dana (the evaluator),
I want the per-repo human/agent commit split with named agents, stated as a lower bound,
So that I can verify the agentic provenance against git itself.

**Acceptance Criteria:**

**Given** a repo's history, **When** the Split computes, **Then** `repositories[].coauthorship` carries `unit: "commit"`, `human_commits`, named `agents[]` (e.g. cursor[bot], Cursor Agent) with counts, and `excluded_bots[]` distinguished from genuine agents. *(FR-3)*

**Given** the AI-co-authored share, **When** presented, **Then** it is labelled a commit-level lower bound **And** the contract reserves the optional forward-compatible `attribution` representation (unused in v1) so v1.5 line-level lands as a MINOR bump. *(FR-3, AD-7)*

**Given** a private repo, **When** emitted, **Then** only aggregate co-authorship counts appear (consistent with the Silhouette), no commit messages. *(AD-9, FR-6)*

**Given** the Split, **When** computed, **Then** it is derived from source on every run, never hand-curated. *(FR-3)*

### Story 2.2: AI-Native Artefact detection + three-class classification

As Dana (the evaluator),
I want detected agentic artefacts classified into workflow/delivery/quality buckets,
So that I see a system around the models, not prompt-theatre.

**Acceptance Criteria:**

**Given** the repos, **When** detection runs, **Then** presence of CLAUDE.md/AGENTS.md/.cursorrules/.claude/mcp is detected and counted per repo into `repositories[].ai_artefacts`, **And** each artefact is assigned exactly one of three classes (workflow_infrastructure / delivery_artefacts / quality_controls). *(FR-4)*

**Given** a private repo, **When** emitted, **Then** only the aggregate artefact counts surface (no path or name). *(FR-4, FR-6)*

**Given** the counts, **When** computed, **Then** they are reconcilable against the repositories from source. *(FR-4)*

---

## Epic 3: A published, inspectable page that backs the DM (fast-track)

A live static page at the Route, deployed from local — provenance-first, audit-noted, inspection-proof — reached by one manual run (the DM fast-track) and kept fresh weekly.
**FRs:** FR-2, FR-7, FR-9, FR-10 · **UX-DR1…6** · **ADs:** AD-8/11/12

### Story 3.1: Scaffold the Astro site + /engineering page rendering from the file

As the builder,
I want a minimal Astro 6 site whose `/engineering` page renders at build time from `build-ledger.json`,
So that the page is static, inspectable, and rebuilt from the one file.

**Acceptance Criteria:**

**Given** a fresh Astro 6 project, **When** scaffolded, **Then** `site/` builds a minimal shell + `src/pages/engineering.astro` **And** the published `build-ledger.json` is served beside the page. *(AD-8)*

**Given** a `build-ledger.json`, **When** the site builds, **Then** the page is fully static HTML/CSS/SVG with numbers present in view-source (no runtime fetch, no charting library). *(AD-8)*

**Given** the page reads `schema_version`, **When** the MAJOR is unsupported, **Then** the page refuses to render rather than mis-render. *(AD-7)*

### Story 3.2: Provenance-first layout with Ledger Metadata + audit notes

As Dana (the evaluator),
I want the hero to lead with provenance and the audit notes visible,
So that I read judgment first and can see how every figure was bounded.

**Acceptance Criteria:**

**Given** the page, **When** rendered, **Then** the Hero leads with the Co-Authorship Split + AI-Native Artefacts and raw LOC is never the first or largest figure **And** the line "This is not a productivity score…" sits near the top. *(FR-2, UX-DR2, UX-DR4)*

**Given** the hero figure, **When** rendered, **Then** the commit-level share shows as an explicit lower bound ("≥ … of commits, commit-level"), never rounded up. *(UX-DR3)*

**Given** the page, **When** rendered, **Then** Ledger Metadata (run timestamp, collector version, schema_version, identities, date range, link to build-ledger.json), the Methodology Note, and the Excluded-from-counts Note are all present and reachable. *(FR-9, UX-DR5)*

### Story 3.3: Visual craft — heatmap, charts, and the restrained aesthetic

As Dana (the evaluator),
I want the page to look as disciplined as the data,
So that the work sample reads as elegant craft, not a stats dump.

**Acceptance Criteria:**

**Given** the aesthetic system, **When** rendered, **Then** it is a restrained light theme — monospace caps labels, large clean numerals, a muted accent, a card-grid layout — with no decoration that doesn't carry information. *(UX-DR1)*

**Given** the activity data, **When** rendered, **Then** a GitHub-style commit-intensity heatmap and commits/month + LOC/month bar charts are drawn as server-generated inline SVG (no charting library, no client JS). *(UX-DR1, AD-8)*

**Given** the integrity stance, **When** rendered, **Then** there is no "SAMPLE DATA" banner and no per-figure trust badges (deliberately cut); integrity is carried by the generated-from-source signal and the audit notes. *(UX-DR5)*

**Given** an empty/no-data Module (e.g. the Mirror sections before Epic 4 lands), **When** rendered, **Then** its section reads as intentional ("no data this run"), not broken. *(AD-3)*

### Story 3.4: Author the Methodology + Excluded-from-counts content

As Sam (the skeptic),
I want a written explanation of exactly how every figure was computed, excluded, and redacted,
So that I can check the method itself, not just the numbers.

**Acceptance Criteria:**

**Given** the Methodology Note, **When** authored, **Then** it explains in prose how repos were discovered, how commits were counted, how user-authored commits were identified, how LOC was calculated, what was excluded, how private repos were redacted, and what is measured-fact vs inferred-indicator. *(FR-9, NFR-1)*

**Given** the Excluded-from-counts Note, **When** authored, **Then** it itemizes exactly what the run excluded (forks, vendored, generated, lockfiles, minified, bot-commits, mirrors) and reflects the run's actual exclusion counts. *(NFR-3)*

**Given** the hero's honest-floor framing, **When** authored, **Then** the Methodology states *why* the commit-level share is a lower bound (trailer-only attribution is one of four layers and misses hand-committed AI code). *(FR-3, UX-DR3)*

**Given** the content, **When** published, **Then** it describes the method only — no private repo name, path, or client name. *(FR-6)*

### Story 3.5: Drill-to-evidence + survives skeptical inspection

As Sam (the skeptic),
I want every figure one click from its evidence and no leak to be findable,
So that I conclude the page is disciplined, not padded.

**Acceptance Criteria:**

**Given** the hero Co-Authorship figure, **When** I expand it, **Then** I see the per-author commit breakdown from `coauthorship` (human + each named agent, with counts) that sums to the headline share, so I can check the arithmetic myself. *(FR-3, UX-DR6)*

**Given** any other headline figure, **When** I interact, **Then** it is one link/expand from its underlying evidence or the Methodology explanation. *(FR-9, UX-DR6)*

**Given** a private repo, **When** I try to find its internals, **Then** I find only a Silhouette (shape + signals, no identifying strings). *(FR-10, FR-6)*

**Given** the page on latest stable desktop Chrome/Safari/Firefox, **When** loaded, **Then** it renders without runtime error **And** no figure on the page lacks a source in `build-ledger.json`. *(FR-10)*

### Story 3.6: Manual fast-track run + pre-built deploy ($0) — the DM milestone

As the builder,
I want one manual command to produce a publishable cut and deploy it pre-built,
So that I can stand a live page behind the GL DM before any schedule is enabled.

**Acceptance Criteria:**

**Given** a manual trigger, **When** the Collector runs, **Then** it produces a complete, redaction-asserted `build-ledger.json` and the page rebuilds from it — without the weekly schedule enabled. *(FR-7)*

**Given** the built `dist/`, **When** deployed, **Then** it is pushed pre-built to the free static host (default Cloudflare Pages via `wrangler pages deploy`) with no host build and no GitHub Actions, $0. *(AD-12)*

**Given** the published cut, **When** complete, **Then** the redacted `build-ledger.json` is committed and pushed (git history = provenance trail) **And** the live page is reachable at the Route. *(AD-1)*

### Story 3.7: Weekly local schedule keeps it fresh

As the builder,
I want a local scheduler to run the pipeline weekly,
So that the page stays current without me, on trusted hardware.

**Acceptance Criteria:**

**Given** a local scheduler (launchd/cron), **When** the weekly trigger fires, **Then** it runs the same pipeline and emits the same `build-ledger.json` shape as a manual run. *(FR-7, AD-1)*

**Given** a scheduled run, **When** it completes, **Then** redaction is applied before publish exactly as on a manual run (fail-closed). *(FR-6)*

**Given** a run is skipped or fails, **When** the page is viewed, **Then** the Ledger Metadata timestamp makes the staleness self-evident. *(NFR-4)*

---

## Epic 4: The Mirror — honest self-insight signals

The builder's true read on his own trajectory — practice, a two-framing retrospective (mirror stays private), and in-flight — lighting up the page's quieter sections without touching the hero path.
**FRs:** FR-5, FR-11, FR-12 · **ADs:** AD-6/9/11

### Story 4.1: Agentic Practice & Efficiency from local logs (aggregate-only)

As the Mirror (Raedmund),
I want aggregate practice + efficiency signals from my local agent logs,
So that I see my craft (cadence, routing, cache discipline, honest cost) without any transcript leaving.

**Acceptance Criteria:**

**Given** local Claude Code + Codex logs, **When** practice computes, **Then** `agentic_practice` carries cadence, model mix, cache-hit ratio, and cost — aggregate only, with NO transcript or session-log text anywhere. *(FR-5, AD-9)*

**Given** a cost figure, **When** emitted, **Then** it carries a labelled pricing source (logged figures, or pinned `config/pricing.yml` with `as_of`), is never estimated, and is omitted if unsourceable; **And** the trend names at least one confounder. *(AD-11, FR-5)*

**Given** logs absent at run time, **When** practice runs, **Then** the Module degrades to `available: false` ("no data this run") rather than failing the run **And** its page section renders accordingly. *(AD-3)*

**Given** the section renders, **Then** it is framed efficiency-as-craft, never a leaderboard or maximization target. *(AD-10)*

### Story 4.2: Two-framing Retrospective — Window publishes, Mirror stays private

As the Mirror (Raedmund),
I want an honest retrospective in two framings,
So that the public sees curated growth while I keep a brutally-honest private read.

**Acceptance Criteria:**

**Given** BMAD memlogs + git, **When** the Retrospective computes, **Then** a curated `retrospective.window_view` is emitted to the public file **And** a brutally-honest `mirror_view` is written ONLY to `mirror.json` in the out-of-tree drawer. *(FR-11, AD-6, AD-5)*

**Given** the public file, **When** published, **Then** it has NO `retrospective.mirror_view` key **And** the Window View quotes no private repo name/path/message. *(AD-6, FR-6)*

**Given** any Retrospective claim, **When** made, **Then** it traces to a memlog entry or git evidence (nothing free-authored) **And** the Window View carries no self-flagellation. *(FR-11)*

**Given** the page renders, **When** viewed, **Then** the Window View appears in its section **And** the Mirror View never appears or links from the page. *(AD-6)*

### Story 4.3: In-Flight from auditable signals only

As the Mirror (Raedmund),
I want a live "what's moving now" view from auditable repo signals,
So that I see genuine momentum, never an aspirational roadmap.

**Acceptance Criteria:**

**Given** live repo signals, **When** In-Flight computes, **Then** `in_flight` carries WIP branches, open issues, draft PRs, in-code work-marker counts, and commit trajectory — each backed by a signal present at run time. *(FR-12)*

**Given** a private repo, **When** emitted, **Then** In-Flight surfaces aggregate-only signals (no branch/issue names or paths). *(FR-12, FR-6)*

**Given** the section renders, **When** viewed, **Then** it is labelled as live signals with the run timestamp, not a roadmap **And** no aspirational or planned-but-unstarted item appears. *(FR-12)*
