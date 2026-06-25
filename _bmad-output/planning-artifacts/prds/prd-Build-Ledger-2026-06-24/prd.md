---
title: Build Ledger
status: final
created: 2026-06-24
updated: 2026-06-25
---

# PRD: Build Ledger

*An auditable proof-of-work ledger for AI-native engineering — a window for others, a mirror for the builder.*

## 0. Document Purpose

This PRD is for the people who will build Build Ledger (the implementing engineer — Raedmund, working agentically — plus any reviewer or downstream architecture/epic workflow that consumes this artifact). It builds directly on two upstream documents and does **not** duplicate them:

- **Brief** — `/Users/raedmund/Projects/Build-Ledger/_bmad-output/planning-artifacts/briefs/brief-Build-Ledger-2026-06-24/brief.md` (positioning, problem, guardrails, vision).
- **Addendum (PRD feeder)** — `/Users/raedmund/Projects/Build-Ledger/_bmad-output/planning-artifacts/briefs/brief-Build-Ledger-2026-06-24/addendum.md`. **All technology-stack and architecture-how detail lives there** (Python collector, GitHub GraphQL/REST, `tokei`/`scc`, static-site rendering, config-file layout, code-exclusion lists, the design-reference mockup `reference-dashboard-mockup.pdf`). This PRD references the addendum rather than restating it, and stays at the level of *capabilities and invariants*.

This PRD precedes the build because two things are invariants you do not want to discover by churning through them: the **`build-ledger.json`** contract every module feeds (§ API Contracts / Public Surface) and the **Redaction Rules** that govern real private client repositories (§ Constraints & Guardrails → Privacy). Both are written here as testable Functional Requirements so collector and Generated Page can be built against a fixed target.

Structure: vocabulary is anchored in the **Glossary** (§3) and used verbatim throughout; features are grouped with **Functional Requirements (FR-N)** nested under each, numbered globally; inferred decisions are tagged inline as `[ASSUMPTION: …]` and collected in the **Assumptions Index** (§9). Adapt-in clusters this product requires — Why Now, Constraints & Guardrails, Cross-Cutting NFRs, API Contracts / Public Surface, Aesthetic & Tone, Platform — appear after the Essential Spine.

---

## 1. Vision

Build Ledger is a public, inspectable record of *how* an AI-native engineer builds software with agents — generated from real repositories, not hand-authored, and refreshed weekly. It turns the usually-invisible evidence of agentic work — agent instruction files, co-authorship metadata, orchestration code, evals, and the shipped systems themselves — into something a skeptic can open and verify. It is an **Evidence Ledger, not a productivity score**: it states what the evidence demonstrates rather than asking the reader to infer it, and every figure is computed from source so none can be hand-flattered.

It serves two readers, and the load-bearing insight is that they are the **same artifact**. The **Window** is the GL hiring manager for the *FDE — Agentic Solutions* role, whose bar is "show me the most complex thing you've shipped, and how you'd build it with agents today," and who screens hard for people who can tell elegant agentic work from fragile or fake. The **Mirror** is the builder himself — a personal instrument that answers "am I growing or just busy? which systems are alive? is my craft deepening?" A ledger genuinely useful to the Mirror reads as *more* authentic to the Window, because self-directed honesty cannot be faked. Build for the Mirror, and the Window comes free.

The headline provenance evidence is the **Co-Authorship Split**, derived from git `Co-authored-by:` trailers. v1 measures this at the **commit level** — **~61.4% of commits AI-co-authored**. State this honestly: that figure is a **lower bound**, not the achievement. Trailers are the *weakest* of four **Attribution Layers** — much AI-written code was hand-committed with no trailer — so commit-level attribution systematically *under-counts*. The true contribution is **line-level**: it is recoverable from the builder's existing local agent session logs (Claude Code + Codex), which already record AI edit/diff events on disk, and is **backfillable across all history**. v1 ships the honest commit-level floor; **line-level Attribution is the v1.5 phase** (see §6), and the document does not overclaim by presenting tomorrow's number today.

Why it matters: the builder is **fully AI-native** (no traditional hand-coding background), so there is no seniority fallback — the work must speak entirely for itself, and the only credible way to make it speak is auditable evidence. A deliberate second-order effect closes the argument: an automated pipeline that discovers repositories, computes the evidence, reflects on itself, and republishes weekly *is* the exact loop the role hires for — ambiguity → working agentic proof → executive-readable output. The artifact demonstrates the very skill it documents.

---

## 2. Target User

### 2.1 Jobs To Be Done

- **(Window — functional)** As a hype-allergic, agentic-native evaluator, I need to verify in minutes that a candidate genuinely ships complex systems *with agents* — and judge whether the work is elegant, fragile, or flawed — without taking a CV's word for it.
- **(Window — social)** I need to defend a hiring decision to peers who are equally skeptical; "the receipts are one click from every claim" is a defensible position, "trust the dashboard" is not.
- **(Mirror — emotional)** As the builder, I need an honest answer to "am I growing or just busy?" that I did not author by hand and therefore cannot flatter.
- **(Mirror — functional)** I need to see where my leverage is, which systems are alive vs decaying, and how my agentic craft is changing over time, so my next build is better-directed.
- **(Both — contextual)** The immediate context is a cold DM application to GL; the durable context is that the same question — "is this real, and how do I know?" — recurs for every future agentic-role evaluator and collaborator.

### 2.2 Non-Users (v1)

- **Non-technical recruiters / generalist hiring screens.** v1 optimizes for an evaluator who *inspects*; a clean PDF for non-technical readers (the "Hiring/Client Pack") is deferred to Vision.
- **Leaderboard / ranking audiences.** Build Ledger is single-subject by construction; it is not a competitive board and explicitly refuses token/spend ranking (the anti-vanity stance).
- **Other engineers wanting to self-host the collector.** v1 is built for one subject's repositories and identity; generalizing into a reusable standard is Vision.
- **Anyone seeking private repository internals.** Reviewers wanting raw private detail are served — if at all — only by the deferred private verification route (Vision), never by the public surface.

### 2.3 Key User Journeys

- **UJ-1. Dana drills from a claim to its git evidence.**
  - **Persona + context:** Dana, the GL *FDE — Agentic Solutions* hiring manager — agentic-native, time-poor, grades taste. Opened the cold DM, clicked through to the Generated Page.
  - **Entry state:** Unauthenticated, first visit, desktop browser, landing at `raedmund.com/engineering`.
  - **Path:** reads the Hero Claim and the "not a productivity score" line; sees the Co-Authorship Split naming `cursor[bot]` and `Cursor Agent` beside the human author; doubts it; follows the inline link from the figure to the underlying git evidence (commit-author + `Co-authored-by:` trailer summary) and the Methodology Note.
  - **Climax:** the number reconciles with inspectable git data and the Methodology Note explains exactly how it was counted and what was excluded — the claim survives inspection.
  - **Resolution:** Dana concludes the agentic provenance is real and well-judged, and replies to the DM. Realizes UJ via FR-2, FR-3, FR-8, FR-9.

- **UJ-2. Sam, the skeptic, tries and fails to find a fabricated number.**
  - **Persona + context:** Sam, a peer evaluator Dana forwarded the page to, assumes any "AI stats page" is inflated and goes hunting for the lie.
  - **Entry state:** Unauthenticated, arriving deep-linked to the repository table / metrics.
  - **Path:** attacks the LOC figure first (the usual padding); finds the prominent "Excluded from counts" Note (forks, vendored, generated, lockfiles, minified, bot-authored commits) already subtracting the obvious inflation; checks a private repository expecting a leak; sees only a Silhouette — shape and signals, no name, no path, no message.
  - **Climax:** every number is either inspectable or honestly bounded, and the private data Sam expected to exploit simply is not exposed. There is no fabricated figure to find.
  - **Resolution:** Sam downgrades from "this is padded" to "this is unusually disciplined," and says so to Dana. Realizes UJ via FR-1, FR-6 (Redaction Rules), FR-9, FR-10.

- **UJ-3. Raedmund reads the Mirror after a build week.**
  - **Persona + context:** Raedmund, the builder, end of a heavy week, wants the truth about his own trajectory, not encouragement.
  - **Entry state:** Reading the same artifact in its Mirror View framing (brutally honest), having just triggered a manual collector run.
  - **Path:** opens the Retrospective sourced from BMAD memlogs + git and reads the honest account of what actually happened; checks Agentic Practice & Efficiency (cadence, model mix, cache-hit ratio, honest cost totals with the pricing source labelled, cost trend with confounders noted) as efficiency-as-craft; glances at In-Flight to see what is genuinely moving.
  - **Climax:** the page tells him something true he had not consciously tracked (e.g. a system going quiet, or efficiency improving), framed as craft rather than spend.
  - **Resolution:** he adjusts where his next build's leverage goes, and returns to the page unprompted later. Realizes UJ via FR-4, FR-5, FR-6.

- **UJ-4. Raedmund fast-tracks one manual cut to back the DM.**
  - **Persona + context:** Raedmund, ready to send the GL DM, before the weekly schedule is switched on.
  - **Entry state:** Collector runnable on demand; schedule not yet enabled.
  - **Path:** triggers one manual collector run; it emits a fresh `build-ledger.json`; the Generated Page rebuilds from it; he confirms the Ledger Metadata (run timestamp, collector version, schema version, link to `build-ledger.json`) is visible and the redaction held.
  - **Climax:** a live, generated, inspectable page exists at the route — enough to stand behind the DM.
  - **Resolution:** he sends the DM linking the page, then enables the weekly schedule so it stays fresh. Realizes UJ via FR-7, FR-8, FR-9.

---

## 3. Glossary

*Downstream workflows and readers must use these terms exactly. FRs, UJs, and SMs use them verbatim; introducing a synonym anywhere is a discipline violation.*

- **Build Ledger** — The product: the automated system (Collector + Generated Page) plus the public artifact it produces at the Route.
- **Evidence Ledger** — The framing of the artifact: an inspectable record of *what the evidence demonstrates*, explicitly **not a productivity score**. Used as a stance, not a feature.
- **Collector** — The automated pipeline that discovers repositories, computes every figure from source, applies the Redaction Rules, and emits `build-ledger.json`. Implementation detail in the addendum.
- **Generated Page** — The static page rendered from `build-ledger.json` at the Route. Never hand-authored; rebuilt whenever a new `build-ledger.json` is produced.
- **Route** — `raedmund.com/engineering`, the public location of the Generated Page.
- **`build-ledger.json`** — The single data contract between Collector and Generated Page. Every Module emits into it. Carries a `schema_version`. Defined concretely in § API Contracts / Public Surface.
- **Module** — One of the seven v1 capability units that compute evidence and feed `build-ledger.json` (see §4). The Module set is fixed for v1.
- **Window** — The external reader: the GL *FDE — Agentic Solutions* hiring manager and evaluators like them. Primary audience.
- **Mirror** — The internal reader: the builder himself, using Build Ledger for self-insight. Co-equal audience.
- **Window View** — The public-facing framing of content: curated, confident, measured. The **only** framing published in the public `build-ledger.json` (`retrospective.window_view`).
- **Mirror View** — The self-facing framing of content: brutally honest. **Private-only** — emitted to a separate private artifact (`private/mirror.json`) consumed locally by the builder, and **never** present in the public `build-ledger.json` nor rendered at the Route. Same sources as the Window View, produced by the same run; the two differ in candour of framing and in where they are written.
- **Co-Authorship Split** — The per-repository human/agent breakdown of commits, derived from commit authors plus `Co-authored-by:` trailers (e.g. the human author, `cursor[bot]`, and `Cursor Agent`). The hero evidence. In v1 this is measured at **commit level** (the unit of attribution is a whole commit); the commit-level figure is a **lower bound** because it can only see commits that carry a trailer. The finer **Line-level Attribution** is a v1.5 phase.
- **Attribution Layer** — One of the ranked methods by which AI authorship can be evidenced, ordered weakest→strongest by coverage: (1) git `Co-authored-by:` trailers (commit-level, the v1 floor); (2) **Line-level Attribution** via session-diff reconciliation; (3) Claude Code OpenTelemetry acceptance signals (the **Acceptance Ratio**); (4) diff heuristics (low-confidence, labelled "inferred"). Each layer is a distinct *method* with its own coverage and confidence; the **git-notes Attribution Store** is the format that records line-level results. Detail in the addendum.
- **Line-level Attribution** — AI authorship measured at the granularity of individual lines (not whole commits), recovered by reconciling AI edit/diff events in local agent session logs against the committed diff, and **backfillable across all history**. The true, higher-coverage measure that the commit-level Co-Authorship Split lower-bounds. A **v1.5** capability (FR-13); not in v1.
- **Acceptance Ratio** — A denominator-aware quality signal: of the lines an agent *offered*, the share the builder *kept*. Sourced from Claude Code OpenTelemetry (`code_edit_tool_decision`) via a local collector. It is what keeps the story about **judgment** rather than volume — for a fully AI-native builder the raw line-level AI % is high by construction, so "how much was offered vs. kept" is the discriminating signal, not "how much AI did." A **v1.5** signal folded into Agentic Practice & Efficiency (FR-5); the metric Build Ledger adopts in place of token/spend counts.
- **git-notes Attribution Store** — A `refs/notes/ai` notes ref carrying line-level AI-attribution provenance that travels with the repository, survives rebase/squash, and is independently verifiable. Adopted as the auditable evidence *format* for Line-level Attribution; a **Vision** capability, not v1 or v1.5.
- **AI-Native Artefact** — A detected file/marker indicating an agentic engineering system: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, a `.claude/` directory, or `mcp`/`.mcp.json`. Classified into the three Artefact Classes.
- **Artefact Class** — One of three buckets an AI-Native Artefact is classified into: **workflow-infrastructure**, **delivery-artefacts**, **quality-controls**.
- **Agentic Practice & Efficiency** — Aggregate-only signals derived by script from local Claude Code and Codex logs: cadence, model mix, cache-hit ratio, honest cost totals (with pricing source labelled), and cost trend (with confounders noted). Framed as efficiency-as-craft, never spend. v1.5 adds the **Acceptance Ratio** as the quality signal here.
- **Retrospective** — The honest account of how the work actually went, sourced from BMAD memlogs (planning) + git (coding). Window View (curated) publishes in `build-ledger.json`; Mirror View (brutally honest) is private-only (see Mirror View).
- **In-Flight** — The auditable view of what is moving now: WIP branches, open issues, draft PRs, TODO/FIXME counts, commit trajectory. Auditable signals only, never aspirational.
- **Display Tier** (`display_tier`) — The privacy level at which a repository is presented, reconciled to the addendum's privacy model. Exactly one of three values: **`public`** (name + metrics), **`redacted`** (generic description, no name), **`aggregate_only`** (Silhouette: shape + signals only, no identifying strings). This is the *sensitivity* axis; it is distinct from the `allowlisted` mechanism. v1 uses only `public` (subject's own public repos) and `aggregate_only` (all private repos), because the Allowlist is empty; `redacted` is defined and representable but unused until a repository is explicitly promoted.
- **Silhouette** — The public representation of a repository at `display_tier: aggregate_only`: shape and signals only (e.g. counts, presence of tests/CI), with **no** name, file path, branch name, commit message, client name, or transcript. (Synonym for the `aggregate_only` tier.)
- **Allowlisted** (`allowlisted`) — A per-repository boolean, separate from `display_tier`, recording that a repository was explicitly promoted by the **Allowlist**. It is the *mechanism* axis: the only way a private repository's `display_tier` may rise above `aggregate_only` (to `redacted` or `public`). In v1 the Allowlist is empty, so `allowlisted` is `false` for every repository.
- **Allowlist** — The explicit, reviewed configuration that is the *only* mechanism by which a private repository's `display_tier` may be promoted above `aggregate_only` (setting `allowlisted: true`). Empty in v1.
- **Redaction Rules** — The safety-critical, testable privacy rules governing what may ever leave a private repository. Defined in § Constraints & Guardrails → Privacy.
- **Pinstack** — The GitHub account/identity the Collector authenticates as to discover and read repositories.
- **Methodology Note** — The published, inspectable explanation of how figures were computed (discovery, commit counting, LOC, exclusions, redaction, AI-evidence detection, measured-fact vs inferred-indicator).
- **Excluded-from-counts Note** — The prominent published list of what is subtracted from counts (forks, vendored deps, generated artefacts, lockfiles, minified files, bot-authored commits, mirrors), inoculating against LOC-inflation objections.
- **Ledger Metadata** — The audit header of a run, surfaced on the Generated Page: run timestamp, Collector version, `schema_version`, GitHub identities included, date range, link to `build-ledger.json`.

---

## 4. Features

*Seven Modules (FR-1 … FR-N), plus the contract and redaction FRs they all depend on. FRs are numbered globally. Tech-how is referenced to the addendum, not restated.*

### 4.1 Repository Collection & Metrics

**Description:** The Collector discovers and reads the subject's repositories — authenticating as **Pinstack** via GitHub GraphQL/REST and inspecting local clones — and computes the conventional facts (repository counts by visibility/status, commit counts, active days, files touched, LOC added/removed/net, languages, test presence, CI presence, migration presence). These facts **substantiate, they do not headline**: volume is supporting cast to provenance. Discovery and exclusion behaviour (which repos are in/out, which paths are skipped) follows the addendum; this feature locks that the figures are computed from source and bounded by the Excluded-from-counts Note. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-1: Compute repository metrics from source

The Collector can discover repositories accessible to **Pinstack** and compute conventional metrics from source, applying the Excluded-from-counts Note before any figure is reported. Realizes UJ-2.

**Consequences (testable):**
- Every numeric figure on the Generated Page traces to a value present in `build-ledger.json` produced by the Collector; no figure is hand-entered.
- Forks, mirrors, vendored dependencies, generated artefacts, lockfiles, minified files, and bot-authored commits are excluded from headline counts, and the exclusion is itemized in the Excluded-from-counts Note rendered on the page.
- Archived repositories are included but labelled as archived; private repositories are included only as Silhouettes unless promoted via the Allowlist (see FR-6).
- Each reported metric is classifiable as measured-fact vs inferred-indicator, and the Methodology Note states which.

**Out of Scope:**
- Cloud usage dashboards (claude.ai / platform.openai.com) — require an export/API key; deferred (addendum).
- A transparent complexity-*scoring* model (weighted dimensions) — deferred to Vision; v1 presents raw inspectable signals only.

#### FR-2: Present volume as supporting cast

The Generated Page can render conventional metrics in a position and weight subordinate to provenance evidence. Realizes UJ-1.

**Consequences (testable):**
- The Hero region leads with provenance (Co-Authorship Split / AI-Native Artefacts), not with repo/commit/LOC totals; raw LOC is not the largest or first figure.
- No bare superlative appears; every superlative is qualified to its measure (e.g. "largest *measured* codebase," "most active *by user-authored commits*").

### 4.2 Git Co-Authorship Analysis (Hero Feature)

**Description:** The hero. The Collector parses commit authors and `Co-authored-by:` trailers across each repository to produce the **Co-Authorship Split** — the human/agent breakdown of commits per repository (e.g. for the flagship system: the human author alongside `cursor[bot]` and `Cursor Agent`). This is the un-fakeable agentic proof, because it lives in the git history itself rather than in any self-report. It is the lead provenance signal the Window inspects first. **v1 measures at commit level** — the unit of attribution is a whole commit, and the headline (~61.4% of commits AI-co-authored) is stated as a **lower bound**: the `Co-authored-by:` trailer is the *weakest* of four **Attribution Layers** (it cannot see AI code that was hand-committed without a trailer), so it under-counts by construction. The honest framing is the point — v1 does **not** claim the line-level number. **Line-level Attribution is a v1.5 phase (FR-13)**, recoverable from the builder's existing local session logs. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-3: Derive the Co-Authorship Split per repository (commit-level, v1)

The Collector can compute, per repository, the **commit-level** split of commits between the human author and named agent authors, from commit author fields and `Co-authored-by:` trailers, and present the resulting AI-co-authored share as an explicit **lower bound** (the v1 floor — one Attribution Layer of four). Realizes UJ-1.

**Consequences (testable):**
- For a repository with known co-authors, the Split names each distinct agent author (e.g. `cursor[bot]`, `Cursor Agent`) and reports its commit attribution count.
- The headline AI-co-authored share is labelled as a **commit-level lower bound** on the page (e.g. "≥ X% of commits, commit-level — line-level is higher"), and the Methodology Note states *why* it is a floor (trailer-only attribution is one of four layers and misses hand-committed AI code). No copy presents the commit-level figure as the total AI contribution.
- Bot-noise authors excluded from headline commit counts (e.g. dependabot) are still distinguishable in the data from genuine agentic co-authors, and the Methodology Note explains the distinction.
- Each figure in the Split has its underlying git evidence — a per-author commit-author/`Co-authored-by:` trailer summary (counts only) — **present on or linked from** the page so a reader can reconcile it directly, without exposing any commit message (see FR-6).
- The Split is computed from source on every run; it is never hand-curated.
- The v1 `coauthorship` shape carries a unit marker (`unit: "commit"`) so the forward-compatible multi-layer `attribution` representation (see § API Contracts) can add line-level without redefining the v1 field (ties to FR-8 versioning).

#### FR-13: Recover Line-level Attribution from local session logs *(v1.5 — not in v1)*

*Next-phase FR, sequenced after the lean v1 ships (see §6.1.1). Listed here to keep the provenance feature coherent and to fix the forward-compatible contract; **explicitly excluded from v1 scope**.*

The Collector can reconcile AI edit/diff events in the builder's local Claude Code (`~/.claude`) and Codex (`~/.codex`) session logs against committed diffs to compute **Line-level Attribution** — AI-attributed lines per repository — **backfilled across history**, emitting aggregate counts only and presenting the result alongside its **Acceptance Ratio** (FR-5). Realizes UJ-1, UJ-3.

**Consequences (testable):**
- Line-level attribution is emitted under the multi-layer `attribution` representation (`method`, `unit: "line"`, `confidence`, `source`) — additive to the v1 commit-level shape, under a `schema_version` MINOR bump, never breaking a page built for v1 (ties to FR-8 versioning).
- Only **aggregate** line counts and ratios are emitted; **no transcript or session-log text** is ever read into the public file or the page (ties to FR-5, FR-6), and for private repositories only Silhouette-consistent aggregates surface (ties to FR-6).
- Any line-level figure is presented with its **Acceptance Ratio** and labelled by Attribution Layer/confidence; a low-confidence diff-heuristic remainder, if shown, is labelled **"inferred"** and never merged into the measured figure.
- The commit-level Co-Authorship Split (FR-3) remains present and is reframed as the lower bound the line-level figure supersedes; the page states the relationship rather than silently swapping numbers.

### 4.3 AI-Native Artefact Detection & Classification

**Description:** The Collector detects **AI-Native Artefacts** — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.claude/` directories, `mcp`/`.mcp.json` — and classifies each into one of three **Artefact Classes**: *workflow-infrastructure* (MCP tools, agent instruction files, eval harnesses, model config, orchestration code), *delivery-artefacts* (implementation plans, session logs, task plans, PR reviews), and *quality-controls* (eval tests, architecture guards, CI checks, prompt regression cases). This shows a *system around the models*, not chatting with them — the anti-"prompt-theatre" framing. Realizes UJ-1.

**Functional Requirements:**

#### FR-4: Detect and classify AI-Native Artefacts

The Collector can detect AI-Native Artefacts across repositories and assign each to exactly one Artefact Class. Realizes UJ-1.

**Consequences (testable):**
- Presence of `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, a `.claude/` directory, or `mcp`/`.mcp.json` is detected and counted per repository.
- Each detected artefact is reported under exactly one of the three Artefact Classes (workflow-infrastructure / delivery-artefacts / quality-controls).
- Detection counts are computed from source and reconcilable against the repositories; for private repositories, only the aggregate signal surfaces (the artefact's path/name is never published — see FR-6).

### 4.4 Agentic Practice & Efficiency

**Description:** The Collector derives **Agentic Practice & Efficiency** from local Claude Code and Codex logs, **aggregate-only and scripted** — it never loads, stores, or publishes transcripts. It reports session cadence, model mix (e.g. Opus/Sonnet/Haiku routing), cache-hit ratio, honest cost totals with the pricing source explicitly labelled, and cost trend over time with confounders named. The entire framing is **efficiency-as-craft** (cache discipline, cost-aware model routing, one's own trend) — never a consumption brag. This is primarily a Mirror signal. **Honesty guard (v1.5):** once Line-level Attribution (FR-13) ships, a fully AI-native builder's line-level AI % is high *by construction*, so a raw "% AI" reads as a volume brag rather than judgment. The **Acceptance Ratio** — of the lines an agent offered, the share kept (from Claude Code OpenTelemetry `code_edit_tool_decision` via a local collector) — is the signal that re-centres the story on judgment, and is the v1.5 quality metric folded into this Module in place of any token/spend figure. Realizes UJ-3. `[ASSUMPTION: local Claude Code and Codex logs remain readable on the machine running the Collector at run time; if absent, this Module degrades to "no data this run" rather than failing the run.]`

**Functional Requirements:**

#### FR-5: Aggregate agentic practice without transcripts

The Collector can compute aggregate practice and efficiency signals (cadence, model mix, cache-hit ratio, cost totals, cost trend) from local agent logs without reading or emitting any transcript content. Realizes UJ-3.

**Consequences (testable):**
- No raw transcript text appears anywhere in `build-ledger.json` or on the Generated Page — only aggregate figures.
- Any cost figure is accompanied by a labelled pricing source — figures the logs record, or a pinned, dated `config/pricing.yml` (with `as_of` + source link); no token usage or cost is invented or estimated, and an unsourceable figure is omitted rather than guessed.
- The cost trend is presented with at least one named confounder (e.g. project mix, model-price changes), never as a bare "spend went up/down."
- Efficiency signals are framed as craft (cache-hit ratio, routing) and are not rendered as a leaderboard rank or maximization target (see SM-C1).
- **(v1.5, with FR-13)** Where Line-level Attribution is shown, it is accompanied by the **Acceptance Ratio** (offered vs. kept), and the Acceptance Ratio — not a raw "% AI" — is the framed quality signal; the Acceptance Ratio is never presented as a maximization target (ties to SM-6, SM-C1).

**Out of Scope:**
- Cursor local data (`state.vscdb`) for token/spend extraction — too messy; the clean Cursor signal is the Co-Authorship Split (addendum).

### 4.5 Retrospective

**Description:** The **Retrospective** presents an honest account of how the work actually went, sourced from BMAD memlogs (planning) + git (coding). It is **judgment on display** — the trait the Window grades. Two framings are produced from the same sources: the **Window View** is curated and confident (growth, not self-flagellation) and is the **only** framing that publishes (it is the `retrospective.window_view` of the public `build-ledger.json`); the **Mirror View** is brutally honest and is **private-only** — emitted to a separate private artifact (`private/mirror.json`) consumed locally by the builder, never published at the Route and never present in the public file. Because the Mirror View is sourced over ~35 private client repos, this private-only rule is a privacy invariant, not a presentation preference. The meta "building Build Ledger" retrospective is itself available and self-evidencing. Realizes UJ-3.

**Functional Requirements:**

#### FR-6 is reserved for Redaction (see §Constraints). The Retrospective FR follows.

#### FR-11: Produce a sourced Retrospective with two framings

The Collector can produce a Retrospective from BMAD memlogs + git in two framings — a curated, confident **Window View** that publishes in `build-ledger.json`, and a brutally-honest **Mirror View** emitted only to the separate private artifact. Realizes UJ-3.

**Consequences (testable):**
- Every Retrospective claim traces to a memlog entry or git evidence; nothing is free-authored narrative without a source.
- Only the Window View publishes: the public `build-ledger.json` carries `retrospective.window_view` and **no** `mirror_view` key; the Mirror View appears only in the private artifact (`private/mirror.json`) and is never linked from the public surface (ties to FR-6).
- The Window View contains no self-flagellation and no aspirational claim; the Mirror View may be brutally honest but still source-bound.
- The published Window View never quotes private commit messages or transcripts and contains no private repo name, path, branch, or client name (see Redaction Rules); it summarizes from sources that are either public or aggregated.

### 4.6 In-Flight

**Description:** The **In-Flight** view shows what is genuinely moving now, from **auditable live repo signals only**: WIP branches, open issues, draft PRs, TODO/FIXME counts, and commit trajectory. It is never an aspirational roadmap — only signals a reader could themselves verify against the repositories. Realizes UJ-3.

**Functional Requirements:**

#### FR-12: Render In-Flight from auditable signals only

The Collector can compute In-Flight from live repository signals (WIP branches, open issues, draft PRs, TODO/FIXME counts, commit trajectory) and exclude any aspirational or planned-but-unstarted item. Realizes UJ-3.

**Consequences (testable):**
- Every In-Flight item corresponds to a signal present in a repository at run time; no item represents intent without a backing signal.
- For private repositories, In-Flight surfaces only aggregate signals consistent with the Silhouette (no branch names, issue titles, or paths — see Redaction Rules).
- The In-Flight section is labelled as live signals with the run timestamp, not as a roadmap.

### 4.7 Collector Pipeline & Generated Page

**Description:** The end-to-end capability: the Collector runs (on a weekly **local schedule** — launchd/cron — **and** on manual trigger), all Modules emit into a single **`build-ledger.json`**, and the **Generated Page** is rendered from that file and published to the **Route**. The page surfaces **Ledger Metadata** (run timestamp, Collector version, `schema_version`, identities included, date range, link to `build-ledger.json`) so it reads as an audit artefact, not a portfolio page. The **fast-track** is explicit: one manual generated cut can back the GL DM before the weekly schedule is enabled. Realizes UJ-1, UJ-2, UJ-3, UJ-4.

**Functional Requirements:**

#### FR-7: Run on schedule and on demand (fast-track)

The Collector can be triggered weekly by a local scheduler (launchd/cron) and manually on demand, where a single manual run produces a publishable cut. Realizes UJ-4.

**Consequences (testable):**
- A manual trigger produces a complete `build-ledger.json` and a rebuilt Generated Page without requiring the weekly schedule to be enabled.
- Enabling the weekly schedule does not change the output contract; a scheduled run and a manual run emit the same `build-ledger.json` shape.
- The Redaction Rules (FR-6) are applied on every run, scheduled or manual, before publication.

#### FR-8: Emit the single `build-ledger.json` contract

The Collector can emit exactly one `build-ledger.json` per run, conforming to the schema in § API Contracts / Public Surface, carrying a `schema_version`, with every Module's output nested under it. Realizes UJ-1, UJ-4.

**Consequences (testable):**
- `build-ledger.json` validates against the documented top-level shape and includes a `schema_version`.
- The Generated Page renders solely from `build-ledger.json`; removing the Collector does not change what the page can display from a given file.
- A missing Module's data (e.g. Agentic Practice with no logs that run) is represented explicitly in the file (e.g. an empty/`null` section), not omitted silently.

#### FR-9: Publish the Generated Page with Ledger Metadata and Methodology

The Generated Page can render at the Route with visible Ledger Metadata, the Methodology Note, and the Excluded-from-counts Note. Realizes UJ-1, UJ-2, UJ-4.

**Consequences (testable):**
- The page displays run timestamp, Collector version, `schema_version`, identities included, date range, and a link to the published `build-ledger.json`.
- The Methodology Note and the Excluded-from-counts Note are present and reachable from the page on every published run.
- Every headline figure is one interaction (link/expand) from either its evidence or the Methodology explanation of how it was derived.

#### FR-10: Survive inspection as a work sample

The Generated Page can be inspected by a skeptical reader without exposing a fabricated figure or breaking. Realizes UJ-2.

**Consequences (testable):**
- No figure on the page lacks a source in `build-ledger.json` and a corresponding Methodology explanation.
- The page renders without runtime error on the latest stable desktop Chrome, Safari, and Firefox (it is itself a graded work sample).
- A reader attempting to find private repository internals via the public surface finds only Silhouettes (see FR-6).

**Notes:** FR numbering is non-contiguous by feature because Redaction (FR-6) is defined in §Constraints for emphasis; FR-11/FR-12 belong to §4.5/§4.6. **FR-13 is a v1.5 next-phase FR** (Line-level Attribution), co-located under §4.2 with the commit-level hero but explicitly out of v1 scope (see §6.1.1). All FRs are globally unique.

---

## 5. Non-Goals (Explicit)

- **Not a productivity score, ever.** Build Ledger is an Evidence Ledger; the page itself says so. It will not compute or display a productivity multiplier, a velocity score, or a "10x" claim.
- **Not a vanity / spend leaderboard.** It will not rank by token totals or cost, and will not present spend as a brag. (This is the explicit anti-vanity positioning vs token-ranking tools.) Concretely rejected, in any version (v1, v1.5, or Vision): **cost/token leaderboards** of any kind; a **"Wrapped"-style spend recap** (year-in-review spend flexing); and **desk-toy spend counters** (a live ticking dollar/token meter). The cross-provider attribution research was filtered for exactly this: Build Ledger adopts the **Acceptance Ratio** as its quality signal *because* it beats token counts, and rejects every spend-as-achievement pattern those tools lean on.
- **Not employer-branded and not a CV.** It is a proof-of-work ledger, not a résumé and not co-branded with any employer.
- **Not an aspirational roadmap.** In-Flight shows only auditable live signals; planned-but-unstarted work does not appear.
- **Not a leak surface.** It will not expose private repository names, file paths, branch names, commit messages, secrets, client names, or raw transcripts under any v1 path.
- **Not re-introducing cut apparatus.** The dataset **trust-modes** (live-verified / redacted-verified / demo) and **per-figure provenance badges** (measured / inferred / redacted / sample / excluded) were deliberately CUT (decision-log Round 3) as over-engineering; auditability here is structural (generated-from-source + Methodology Note), so they will not be reintroduced in v1.

---

## 6. MVP Scope

### 6.1 In Scope

- The **seven v1 Modules** (FR-1 … FR-5, FR-11, FR-12): Repository Collection & Metrics; Git Co-Authorship Analysis (hero); AI-Native Artefact Detection & Classification; Agentic Practice & Efficiency (aggregate-only); Retrospective; In-Flight.
- **Commit-level Co-Authorship Split only** (FR-3): the hero provenance ships at the commit level, with its AI-co-authored share stated as an explicit **lower bound** (the v1 floor). **Line-level Attribution is explicitly *not* in v1** — it is v1.5 (see §6.1.1) — keeping v1 lean and shippable against the existing modules.
- The **Collector Pipeline & Generated Page** (FR-7 … FR-10): every figure computed from source → single `build-ledger.json` → Generated Page at the Route.
- **Weekly refresh** (local scheduler — launchd/cron) **and manual trigger**, with visible Ledger Metadata.
- **Safe-by-default Redaction** (FR-6): private repositories render as Silhouettes (`display_tier: aggregate_only`); the Allowlist is the only promotion path and ships **empty** in v1, so every private repository is a Silhouette; a whole-document redaction assertion gates publish; rules reviewed before any private clone.
- The **fast-track**: one manual generated cut can back the GL DM before the weekly schedule is enabled.
- The **Methodology Note** and the prominent **Excluded-from-counts Note**.
- **Provenance-first presentation**: lead with judgment/provenance (Co-Authorship Split, AI-Native Artefacts, tests/CI/migrations); volume demoted to supporting cast.

### 6.1.1 Next phase — v1.5 *(line-level, after the lean v1 ships)*

Deliberately **out of v1** to keep the first cut lean; sequenced as the immediate next phase because the data already exists locally and the v1 schema is built forward-compatibly to absorb it (see § API Contracts).

- **Session-diff reconciliation → Line-level Attribution** (FR-13). Parse the builder's existing local Claude Code (`~/.claude`) and Codex (`~/.codex`) session logs, match AI edit/diff events to commits, and compute **line-level** AI attribution — **backfilled across all history**. This turns the commit-level lower bound into the true measure. It is solo/local/privacy-feasible because the data is already on disk and only aggregates are emitted (no transcripts; ties to FR-5/FR-6).
- **Acceptance Ratio** (extends FR-5). The offered-vs-kept quality signal from Claude Code OpenTelemetry (`code_edit_tool_decision`), so the line-level story stays "judgment," not "look how much AI did" (the honesty guard).
- These v1.5 additions ship under a **`schema_version` MINOR bump** via the forward-compatible `attribution` representation; they do not change the v1 `build-ledger.json` shape (§ API Contracts → Versioning).

### 6.2 Out of Scope for MVP *(deferred to Vision)*

- **Full per-figure badge UI** and **dataset trust-modes** — deliberately cut (see Non-Goals); structural auditability replaces them.
- **The six-pack evidence ecosystem** (Repository / Architecture / AI-Native / Data Systems / Hiring-Client evidence packs) — `[NOTE FOR PM]` the AI-Native and Architecture packs are emotionally load-bearing for the Window; revisit first if timeline permits.
- **A transparent complexity-scoring model** (weighted dimensions) — a self-chosen weighting is an opinion a skeptic can discount; v1 ships raw inspectable signals instead.
- **Momentum / decay windows** (7d / 30d / 90d / trailing-12m comparisons) — deferred; In-Flight covers "what's moving now" for v1.
- **The private redacted verification bundle** (on-request reviewer pack) — deferred; Silhouettes + Methodology are the v1 privacy posture.
- **Export packs** (XLSX / PDF / CSV public summaries) and **auto-PR to raedmund.com** — deferred; the Generated Page is the v1 deliverable.
- **Leaderboard breadth / multi-subject generalization** — Vision; v1 is single-subject.
- **git-notes Attribution Store** (`refs/notes/ai`) — Vision; a repo-travelling, rebase/squash-surviving, independently-verifiable store is the eventual auditable *format* for Line-level Attribution, layered on after v1.5 produces line-level results.
- **Claude Code OpenTelemetry collector (standing)** — Vision; a local OTLP collector capturing `code_edit_tool_decision` going-forward (beyond the v1.5 Acceptance-Ratio read) is deferred infrastructure.
- **Cursor / Copilot acceptance APIs** — **explicitly out, all versions.** Their acceptance/usage data is org/team-admin-gated and not available to a solo user; the clean Cursor signal remains the commit-level Co-Authorship Split, and line-level coverage comes from the local Claude Code/Codex logs instead.

---

## 7. Success Metrics

*Each SM cross-references the FR(s) it validates. Counter-metrics counterbalance specific primary/secondary metrics and are as load-bearing as the primary.*

**Primary**

- **SM-1**: **The cold GL DM earns a substantive human reply.** Definition: a real, non-form, human response to the DM that links the Generated Page (not silence, not an auto-reply). Target: ≥ 1 substantive reply from the GL application. Validates the artifact end-to-end: FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12 — everything downstream follows from clearing it.

**Secondary**

- **SM-2**: **A skeptical agentic-native reader finds it credible.** Definition: an inspecting reader concludes the methodology holds and nothing over-claims, and the published `build-ledger.json` they open is well-formed and schema-valid (a malformed or contract-breaking file is itself a credibility failure). Validates FR-1, FR-8, FR-9, FR-10.
- **SM-3**: **AI-provenance is legible in under one minute.** Definition: a first-time reader can identify the agentic provenance (Co-Authorship Split / AI-Native Artefacts) within ~60 seconds of landing. Validates FR-2, FR-3, FR-4.
- **SM-4**: **It survives a "fragile or flawed?" read.** Definition: a skeptic attempting to find a fabricated number or a leak fails on both, and the page does not break — on the fast-track manual cut that backs the DM as well as on a scheduled run. Validates FR-6, FR-7, FR-9, FR-10. (Realizes UJ-2.)
- **SM-5 (Mirror)**: **Raedmund returns to it unprompted.** Definition: the builder revisits the page for self-insight without an external trigger. Validates FR-4 (Agentic Practice), FR-11 (Retrospective), FR-12 (In-Flight). (Realizes UJ-3.)
- **SM-6 (quality signal — v1.5)**: **The Acceptance Ratio carries the AI-contribution story, not raw "% AI."** Definition: once Line-level Attribution ships (FR-13), wherever a line-level AI share appears it is paired with the **Acceptance Ratio** (offered vs. kept), so a reader reads judgment (what was kept) rather than volume (how much was generated). Validates FR-5 (Acceptance Ratio) and FR-13. This is the honesty guard made measurable; it is a quality bar, **not** a number to maximize (see SM-C1).

**Counter-metrics (do not optimize)**

- **SM-C1**: **Raw token totals / cost — and spend-as-spectacle.** Must *not* be maximized or framed as achievement; spend appears only as efficiency-as-craft with confounders named. Explicitly rejected in any version: **cost/token leaderboards**, a **"Wrapped"-style spend recap**, and **desk-toy spend counters** (live ticking meters). The **Acceptance Ratio** (SM-6) is the sanctioned quality signal precisely because it beats token counts; the **Acceptance Ratio itself is also not a maximization target**. Counterbalances any drift in FR-5 toward a spend brag and protects the anti-vanity stance behind SM-2.
- **SM-C2**: **Lines of code (LOC).** Must *not* be inflated or headlined; bounded by the Excluded-from-counts Note and demoted below provenance. Counterbalances FR-1/FR-2 against the "nicer GitHub profile" failure mode.
- **SM-C3**: **Session counts / repo count as vanity.** Must *not* be treated as a score; breadth substantiates, it does not headline. Counterbalances FR-1 and FR-5.

*The counter-metrics are the discipline: optimizing any of them turns the Evidence Ledger back into the very vanity artifact it exists to refute, which would fail SM-1 with this specific reader.*

---

## 8. Open Questions

*Two former open questions that sat directly on the locked invariants have been **resolved** and moved into the decided sections; they are recorded here for traceability, then the genuinely-open questions follow.*

**Resolved (no longer open):**

- **Allowlist seed for v1 → resolved: none.** v1 ships with an **empty Allowlist**: every private repository defaults to `display_tier: aggregate_only` (a Silhouette) and `allowlisted: false`. No private repository is promoted for the first public cut, so no client Redaction Rules need per-repo review against named client constraints (e.g. Client A / Client B) before the first clone. (Decided in §6.1 *Safe-by-default Redaction*, the Glossary *Allowlist*/*Display Tier* entries, and FR-6.)
- **Mirror View exposure → resolved: no — the Mirror View is private-only.** Only the curated Window View publishes at the Route; the brutally-honest Mirror View is emitted to a separate private artifact (`private/mirror.json`) consumed locally and is never present in the public `build-ledger.json` nor rendered at the Route. (Decided in §4.5/FR-11, FR-6, and § API Contracts.)

- **Cost-source authority → resolved (architecture spine, 2026-06-25).** Cost figures come from what the Claude Code / Codex logs already record; where unrecorded, from a **pinned, dated, published** price table shipped in-repo as `config/pricing.yml` (with a source link). The pricing source + `as_of` date are shown on the page; cost is **never** estimated, and an unsourceable figure is omitted rather than guessed. (Ties FR-5, SM-C1; see ARCHITECTURE-SPINE AD-11.)
- **Generated Page hosting/runtime → resolved (architecture spine, 2026-06-25).** The Route is served by a **static host, free tier** — recommended default **Cloudflare Pages** (host swappable) — with the site **built locally and deployed pre-built** via `wrangler` ($0, no host build minutes, no GitHub Actions). (See ARCHITECTURE-SPINE AD-8, AD-12.)
- **Runtime mechanism → reconciled (architecture spine, 2026-06-25).** The weekly Collector runs on a **local scheduler** (`launchd`/cron), **not** a GitHub Action: the FR-6 privacy invariant forbids cloning ~35 private client repositories onto a third-party CI runner (redaction protects the *output*, not the *clone*), so the GitHub token is a **local** secret. A static host's build may still run in CI because it only ever sees the already-redacted public `build-ledger.json`. This supersedes the earlier "weekly GitHub Action" wording throughout. (See ARCHITECTURE-SPINE AD-1.)

**Still open:**

1. **Representative systems framing.** Are the candidate named systems (Meshic, geo-ingest, mcp-toolbelt) surfaced as a "representative systems" treatment within v1's provenance-first page, or is that presentation deferred with the six-pack to Vision? *(Architecture spine flags this as a page-content/UX decision, not a structural invariant — addable later via a non-breaking schema MINOR bump.)*

---

## 9. Assumptions Index

- **§4.4 (FR-5)** — Local Claude Code and Codex logs are readable on the Collector's machine at run time; if absent, the Module degrades to "no data this run" rather than failing the run.
- **§8 (resolved)** — The Generated Page is statically hosted on a free-tier static host (default Cloudflare Pages, swappable), built locally and deployed pre-built; no backend. The Collector runs **locally** (launchd/cron), not in CI, and the GitHub token is a local secret. (Architecture spine AD-1, AD-8, AD-12.)
- **§Cross-Cutting NFRs (Performance)** — No hard latency SLA in v1 beyond "fast static page"; detailed budgets live in the addendum if needed.
- **§Platform (mobile)** — Mobile is supported best-effort via the static layout but is not a v1 optimization target.
- **(Promoted from former §8 Q1, now a decided default rather than an open assumption):** v1 ships with an empty Allowlist — every private repository is a Silhouette (`display_tier: aggregate_only`, `allowlisted: false`). Recorded under §8 *Resolved* and enforced by FR-6.
- **(Carried from upstream, now treated as settled inputs, not open assumptions):** audience is "GL + evaluators like them"; the success bar is a substantive human reply; significant builds are auto-derived from source (not hand-curated); the Route is `/engineering`. These were resolved in the brief's decision log and are stated here for traceability.

---

# Adapt-In Clusters

## Why Now

The timing is load-bearing, not incidental. 2025–26 is defined by an **AI-credibility gap**: AI-assisted coding adoption is high and still climbing, while *trust* in AI-generated work is falling, and "vibe coding" has become a hiring **red flag** rather than a credential. Evaluators want to separate genuine agentic practitioners from people who merely prompt — and there is no standard instrument that shows *how* someone works with agents, only *that* they committed code. Build Ledger's "auditable receipts for agentic work" thesis exists precisely because that gap is now acute. The trigger is also concrete and live: an open GL *FDE — Agentic Solutions* application whose explicit bar — shipped complexity *and* method, with a pre-screen against anyone uneasy that "AI writes most of the code" — is this exact pain said aloud. Build for this moment and this reader, and the artifact has its first real user on day one.

## Constraints & Guardrails

### Privacy *(safety-critical — the #1 reason this PRD precedes the build)*

The subject's repositories include ~35 real **private client** repositories (with real client names). The Redaction Rules below are invariants, written and **reviewed before any private repository is cloned**, and are encoded as a first-class Functional Requirement so they are testable, not aspirational.

#### FR-6: Enforce the Redaction Rules (safe-by-default)

The Collector must apply the Redaction Rules to every repository on every run before any output is published, defaulting every private repository to `display_tier: aggregate_only` (a Silhouette), and must run a whole-document redaction assertion over the public `build-ledger.json` before it ships. Realizes UJ-2.

**Consequences (testable):**
- A private repository renders on the Generated Page as a **Silhouette** (`display_tier: aggregate_only`) — shape and signals only (e.g. presence of tests/CI, aggregate counts) — and **never** exposes any of: repository name, file path, branch name, commit message, secret, client name, proprietary project name, or private issue/PR content.
- **Global redaction invariant:** **no object anywhere in the public `build-ledger.json`** — including `repositories[]`, `aggregates`, `agentic_practice` (especially the free-text `cost.confounders` notes), `retrospective.window_view`, and `in_flight` — contains a private repository name, file path, branch name, commit message, client name, proprietary project name, secret, or raw transcript text. This is enforced by a redaction pass plus an assertion over the **whole document** before publish; if the assertion fails, the run does not publish (fail-closed).
- **The `mirror_view` never publishes:** the brutally-honest Mirror View is written only to the separate private artifact (`private/mirror.json`, see § API Contracts) and is **never** present in the public `build-ledger.json`, never linked from it, and never rendered at the Route. The published `build-ledger.json` has no `retrospective.mirror_view` key (ties to FR-11).
- **No raw agent-log transcript** is ever published or stored in `build-ledger.json`; agent-log signals are aggregated by script only (ties to FR-5).
- The **Allowlist** is the *only* mechanism that can promote a private repository's `display_tier` above `aggregate_only` (setting `allowlisted: true`); absent an Allowlist entry, a private repository stays a Silhouette by default. v1 ships with an empty Allowlist, so every private repository is `aggregate_only` and every repository's `allowlisted` is `false`.
- Redaction is applied **before** publication on both scheduled and manual runs; a run that cannot apply redaction does not publish.
- The Redaction Rules are documented and were reviewed prior to the first private clone; the Methodology Note states the redaction posture.
- A test fixture exercising all five public blocks (`repositories[]`, `aggregates`, `agentic_practice`, `retrospective`, `in_flight`) — including a "private" repository — produces a published file that contains none of the prohibited fields (name/path/branch/message/secret/client name/transcript) and has no `retrospective.mirror_view` key.

### Safety

- **Secrets never transit the public surface.** Authentication to Pinstack uses a secret token held **locally** (the builder's `gh`/env auth on the trusted machine — never on a third-party runner); the token and any secret discovered in a repository never appear in `build-ledger.json` or on the page.
- **Fail-closed publication.** Any run that cannot complete redaction or cannot produce a schema-valid `build-ledger.json` must not publish (ties to FR-6, FR-8).
- **The page is a work sample.** It must not break under inspection; a broken or over-claiming page is a worse signal than no page (ties to FR-10).

### Cost

- **Efficiency-as-craft only.** Any cost figure is framed as craft (cache-hit discipline, model routing, own trend), never as consumption; confounders are named (ties to FR-5, SM-C1).
- **No invented economics.** Token usage and cost appear only where auditable/exportable; nothing is estimated or fabricated (ties to FR-5).
- **Lean operational cost.** v1 is a static page plus a weekly **local** Collector run; no backend, no standing infrastructure, $0 hosting (free-tier static host).

## Cross-Cutting NFRs

- **Auditability (system-wide):** every published figure is reconcilable from source or from the Methodology Note; "every claim is inspectable, or it doesn't ship" is a release gate, not a nicety.
- **Reproducibility:** a given `build-ledger.json` fully determines the Generated Page; re-rendering the same file yields the same page.
- **Determinism of exclusions:** the Excluded-from-counts Note reflects exactly what the Collector excluded on that run.
- **Freshness & observability:** Ledger Metadata (run timestamp, Collector version, `schema_version`) is visible on every published run so staleness is self-evident.
- **Performance (modest):** the weekly **local** run completes in a few minutes on the builder's machine; the static page loads fast on a current desktop browser. `[ASSUMPTION: no hard latency SLA in v1 beyond "fast static page"; detailed budgets live in the addendum if needed.]`
- **Portability of the contract:** `build-ledger.json` is the stable boundary; collector internals (LOC tool, language detection) may change without changing the page, provided the schema holds.

## API Contracts / Public Surface

The **`build-ledger.json`** file is the entire public surface and the only contract between Collector and Generated Page. It is defined concretely so both sides can be built against it without churn. (Field-level encoding detail and the code-exclusion lists live in the addendum; this section locks the **top-level shape, the load-bearing keys, and versioning**.)

**Top-level shape (v1):**

```json
{
  "schema_version": "1.0.0",
  "ledger_metadata": {
    "generated_at": "<ISO-8601 timestamp>",
    "collector_version": "<semver>",
    "schema_version": "1.0.0",
    "identities_included": ["Pinstack"],
    "date_range": { "first_commit": "<date>", "latest_commit": "<date>" },
    "data_url": "<link to this build-ledger.json>",
    "methodology_url": "<link to Methodology Note>"
  },
  "repositories": [
    {
      "id": "<stable opaque id>",
      "display_tier": "public | redacted | aggregate_only",
      "allowlisted": false,
      "label": "<name ONLY if display_tier=public; generic description if redacted; omitted/null if aggregate_only>",
      "category": "<optional generic category for non-public repos, e.g. 'Private software system'; never an identifying string>",
      "status": "active | archived",
      "metrics": { "commits": 0, "active_days": 0, "files": 0,
                   "loc_added": 0, "loc_removed": 0, "loc_net": 0 },
      "signals": { "has_tests": false, "has_ci": false, "has_migrations": false },
      "coauthorship": {
        "unit": "commit",
        "human_commits": 0,
        "agents": [ { "author": "cursor[bot]", "commits": 0 } ],
        "excluded_bots": [ { "author": "dependabot", "commits": 0 } ]
      },
      "ai_artefacts": {
        "workflow_infrastructure": 0,
        "delivery_artefacts": 0,
        "quality_controls": 0
      }
    }
  ],
  "aggregates": {
    "repo_counts": { "public": 0, "private": 0, "archived": 0, "active": 0 },
    "languages": [ { "name": "Python", "share": 0.0 } ],
    "totals": { "commits": 0, "user_authored_commits": 0, "loc_net": 0 }
  },
  "agentic_practice": {
    "available": true,
    "cadence": {}, "model_mix": [], "cache_hit_ratio": 0.0,
    "cost": { "total": 0.0, "pricing_source": "<label>",
              "trend": [], "confounders": ["<named confounder>"] }
  },
  "retrospective": { "window_view": [] },
  "in_flight": {
    "wip_branches": 0, "open_issues": 0, "draft_prs": 0,
    "todo_fixme": 0, "commit_trajectory": []
  },
  "exclusions": {
    "forks": 0, "vendored": 0, "generated": 0, "lockfiles": 0,
    "minified": 0, "bot_commits": 0, "mirrors": 0
  }
}
```

**Load-bearing keys (must exist, stable for v1):** `schema_version`, `ledger_metadata`, `repositories[]` (each with `display_tier`, `allowlisted`, `metrics`, `signals`, `coauthorship` carrying `unit: "commit"`, `ai_artefacts`), `aggregates`, `agentic_practice` (with `available` flag), `retrospective` (with `window_view` **only** — see below), `in_flight`, `exclusions`.

**Forward-compatible attribution representation (v1 ships commit-level; v1.5 adds line-level — non-breaking).** v1's `coauthorship` is the commit-level Co-Authorship Split, tagged `unit: "commit"`. The schema reserves a multi-layer **`attribution`** representation so Line-level Attribution (FR-13) and the Acceptance Ratio (FR-5) land in **v1.5 under a `schema_version` MINOR bump** *without altering any v1 key*. The v1.5 addition is an **optional** `attribution` array per repository (and an aggregate mirror), each entry shaped:

```jsonc
// v1.5+ ONLY — additive, optional; absent in v1 files. Each Attribution Layer is one entry.
"attribution": [
  { "method": "coauthored_by_trailer",   "unit": "commit", "confidence": "measured", "source": "git", "ai_share": 0.0 },
  { "method": "session_diff_reconcile",  "unit": "line",   "confidence": "measured", "source": "claude_code+codex_logs",
    "ai_lines": 0, "total_lines": 0, "acceptance_ratio": 0.0 },
  { "method": "diff_heuristic",          "unit": "line",   "confidence": "inferred", "source": "diff", "ai_lines": 0 }
]
```

Rules: `method` ∈ {`coauthored_by_trailer`, `session_diff_reconcile`, `otel_decision`, `diff_heuristic`}; `unit` ∈ {`commit`, `line`}; `confidence` ∈ {`measured`, `inferred`} (a `diff_heuristic` entry is always `inferred` and labelled as such on the page); `source` records provenance. A v1 page ignores `attribution` if present; a v1.5 page prefers `attribution` (line-level + Acceptance Ratio) and falls back to `coauthorship` (commit-level lower bound) when `attribution` is absent. Because the addition is a new optional key only, it is a **MINOR** bump (see Versioning) and never breaks a page built for v1. **No raw transcript or session-log text ever enters `attribution`** — aggregate counts/ratios only (binds to FR-5, FR-6).

**`mirror_view` is never in the public file (binds to FR-6, FR-11).** The public `retrospective` object carries **only** `window_view`. The brutally-honest `mirror_view` is emitted to a **separate private artifact** that is never published and never linked from the Generated Page or from `build-ledger.json`:

```json
// private/mirror.json — PRIVATE-ONLY, never published, never linked from build-ledger.json
{
  "schema_version": "1.0.0",
  "generated_at": "<ISO-8601 timestamp>",
  "mirror_view": []
}
```

The publish step writes `build-ledger.json` to the public Route and writes the mirror artifact only to a `private/`-scoped path the collector keeps local; the two are produced by the same run but only the public file is ever served. "The mirror never publishes" is therefore a machine-checkable consequence: the published `build-ledger.json` has no `retrospective.mirror_view` key (see FR-6 and FR-11).

**Global redaction contract (binds to FR-6).** Before publication, the Collector runs a single redaction pass over the **entire** `build-ledger.json` document and asserts that **no object anywhere in the public file** — including `repositories[]`, `aggregates`, `agentic_practice` (especially the free-text `cost.confounders` notes), `retrospective.window_view`, and `in_flight` — contains any of: a private repository name, file path, branch name, commit message, client name, proprietary project name, secret, or raw transcript text. For any repository whose `display_tier` is `redacted`, `label` is a generic description only and carries no identifying string; for `aggregate_only`, `label` is omitted/`null` and only `metrics`/`signals`/aggregate `coauthorship` counts appear. Free-text-bearing blocks (`agentic_practice` confounders, `in_flight`, aggregate language/model labels) carry only aggregate integers/labels drawn from a controlled vocabulary. The publish step fails closed if the assertion does not hold. This whole-document assertion is the machine-checkable expression of the Redaction Rules.

**Module-availability contract (binds to FR-8):** a Module with no data for a run is represented explicitly — e.g. `agentic_practice.available = false` with empty sub-objects — never omitted, so the Generated Page can render "no data this run" rather than guess.

### Versioning & Compatibility

- **`schema_version` is semantic (`MAJOR.MINOR.PATCH`).** It appears both at the top level and inside `ledger_metadata` (the latter is what the page displays).
- **Additive changes** (new optional keys) bump **MINOR** and must not break a Generated Page built for an earlier MINOR of the same MAJOR. **Worked example (v1.5):** adding the optional `attribution` representation (Line-level Attribution + Acceptance Ratio, FR-13/FR-5) is a MINOR bump to `1.1.0` — the v1 `coauthorship` (commit-level) key is untouched, so a v1 page still renders a v1.5 file (ignoring `attribution`) and a v1.5 page reading a v1 file simply finds no `attribution` and shows the commit-level lower bound.
- **Breaking changes** (renaming/removing a load-bearing key, changing a field's meaning, tightening the redaction contract in a non-back-compatible way) bump **MAJOR**; the Generated Page declares the MAJOR it supports and refuses to render an unsupported MAJOR rather than mis-render.
- **PATCH** is reserved for clarifications that change neither shape nor meaning.
- The Generated Page reads `schema_version` first and renders against it; this is what lets collector and page evolve independently (Cross-Cutting NFR: portability of the contract).

## Aesthetic & Tone

- **Restrained, numerical, auditable.** Clean light theme; monospace caps labels with large clean numerals; muted accent; GitHub-style commit-intensity heatmap; card-grid layout. Reference: `reference-dashboard-mockup.pdf` (addendum) — adopt the *visual language*, but correct its volume-led hero.
- **Provenance-first hero; volume is supporting cast.** The mockup's instinct to lead with repos/commits/LOC is explicitly overridden: lead with the Co-Authorship Split and AI-Native Artefacts (the decisive Round-2 resolution). Comprehensive data is fine; comprehensive *emphasis* is not.
- **Anti-"AI wizard."** No "wizard"/magic language, no productivity multipliers, no unverifiable token estimates, no inflated LOC, no vanity metrics without context. Superlatives stay measured ("largest *measured* codebase").
- **Honest floor framing for the hero figure.** The commit-level AI-co-authored share (~61.4%) is rendered as a **lower bound**, never as "the" AI contribution — phrase it as a floor ("≥ … of commits, commit-level") with a one-line pointer that line-level is higher and is the next phase. Under-claiming the headline number *is* the credibility move with this reader; do not let UI copy round it up to the line-level story before FR-13 ships.
- **Voice:** confident but boring-on-purpose where it counts; the credibility comes from the reader being able to check, not from the prose. The single best framing line belongs near the top: *"This is not a productivity score. It is an evidence ledger showing sustained, inspectable engineering activity across real repositories."*
- **Integrity cues kept; theatre dropped.** Keep the generated-from-source signal, the Methodology Note, and the Excluded-from-counts Note. Do **not** use a bare "SAMPLE DATA" banner, and do **not** add per-figure trust badges (cut — see Non-Goals).

## Platform

- **Web, static, public.** A static Generated Page at the Route (`raedmund.com/engineering`), rendered from `build-ledger.json`, with no backend.
- **Refresh:** weekly via a **local scheduler** (launchd/cron), plus manual trigger; the fast-track (one manual cut) backs the DM before the schedule is enabled.
- **Reader target:** latest stable desktop Chrome / Safari / Firefox first (the Window inspects on desktop); the page must not break under inspection. `[ASSUMPTION: mobile is supported best-effort via the static layout but is not a v1 optimization target.]`
- **Collector runtime / hosting specifics:** addendum (and Open Question §8 Q5).
