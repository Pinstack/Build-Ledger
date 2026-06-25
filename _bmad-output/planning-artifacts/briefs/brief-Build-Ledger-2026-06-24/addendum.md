# Build Ledger — Addendum (Downstream Detail)

> Preserved from Raedmund's original "Prompt Brief" (2026-06-24). This is implementation and
> solution detail that belongs in the downstream PRD and architecture, not in the 1–2 page
> product brief. Captured verbatim-in-substance so nothing is lost. These are not locked
> decisions — they are the user's starting proposals.

## Target Destination
- Primary route: `raedmund.com/engineering`
- Alternatives considered: `/build-ledger`, `/engineering-ledger`, `/work-ledger`
- Preferred product name: **Build Ledger**

## Recommended Architecture (two layers)
1. **Collector / Ledger project** — repo `raedmund-engineering-ledger`. Responsibilities: GitHub API collection; local repo scanning; LOC/language analysis; commit/activity analysis; complexity-signal detection; AI-evidence detection; privacy/redaction handling; generate public dashboard JSON; generate private raw evidence outputs.
2. **Raedmund.com presentation layer** — consume generated JSON; render charts + summary cards; show public-safe repo/activity evidence; downloadable public summary; never expose secrets, private repo names, or sensitive commit data.

## Weekly Automation (scheduled GitHub Actions, once/week, manual run supported)
Pipeline: authenticate via secret token → fetch repo metadata → clone/inspect permitted repos → scan codebases → calculate metrics → apply privacy/redaction → generate dashboard JSON → generate optional XLSX/PDF/CSV → publish public data → optionally open a PR to Raedmund.com with the updated dataset.

## Privacy Model (three visibility levels)
| Visibility | Public Dashboard | Private Evidence Pack |
| --- | --- | --- |
| Public | repo name + metrics visible | full data |
| Redacted | generic repo description visible | full data |
| Private | aggregate metrics only | full data |

Private repos must never expose: repo names (unless explicitly allowed), commit messages, branch names, file paths, secrets, client names, proprietary project names, private issue/PR content.

## Repository Discovery
Include: public repos; private repos where the token allows; archived repos (marked as archived); solo repos; collaborative repos (user-authored work separated where possible).
Exclude/flag: forks; mirrors; vendored dependency repos; toy repos; generated repos; abandoned experiments.

## Code Exclusions (where practical)
`node_modules`, `.venv`, `venv`, `dist`, `build`, `.next`, `coverage`, lockfiles, vendored deps, generated artefacts, minified files, binary files, large data files, cache directories.

## Dashboard Sections (proposed)
1. **Headline metrics** — repos analysed; public/private/active/archived counts; first & latest commit date; active coding days; total commits; user-authored commits; files touched; LOC added/removed/net; languages; test files; CI/CD workflows; DB migrations; docs/ADR files; AI-native evidence files.
2. **Activity over time** — weekly/monthly: commits; active days; repos active; LOC touched; files touched; language mix over time.
3. **Repository table** — columns: Repository/Label, Visibility, Status, First Seen, Last Active, Active Days, Commits, LOC, Main Stack, Complexity Signals. Redacted labels for private repos unless configured otherwise.
4. **Language & stack breakdown** — Language/Tech, Repositories, Files, LOC, Share. (Python, TS, JS, SQL, React, FastAPI, PostGIS, Alembic, Docker, Shell, YAML, Markdown, CI providers, test frameworks, orchestration.)
5. **Complexity signals** — counts per: API services; frontend apps; DB migrations; geospatial/GIS; data ingestion pipelines; scraping systems; MCP/server tooling; CI/CD workflows; Docker/deploy config; test suites; ADRs/specs/docs; scheduled jobs/orchestration. Goal: distinguish real systems from toy repos.
6. **AI-native development evidence** — agent instruction files; prompt briefs; Codex logs/artefacts; Claude Code artefacts; Cursor config; MCP tools; AI eval harnesses; LLM orchestration code; model config; usage exports; invoices/cost reports; structured task plans; implementation logs. **Do not invent token usage** — exact token/spend only where exportable/auditable.
7. **Significant builds** — strongest by category: largest codebase; most active; most complex architecture; most tests; most data-heavy; most AI-native; most recent momentum.

## Output Artefacts
**Public:** `public/build-ledger.json`; static dashboard page; downloadable public summary PDF; downloadable public XLSX summary.
**Private (never published):** `private/repos_raw.csv`; `commits_raw.csv`; `language_raw.csv`; `complexity_signals.csv`; `ai_evidence.csv`; `exclusions_log.csv`; `methodology.md`.

## Suggested Tech Stack
**Collector:** Python; GitHub GraphQL (+ REST where useful); `git`; `tokei` or `scc` for LOC/language; pandas/openpyxl for XLSX; optional Playwright for screenshots only if needed.
**Dashboard:** static JSON; Astro / Next.js / plain static React; lightweight charts; no backend; deployable via GitHub Pages, Cloudflare Pages, Vercel, or existing Raedmund.com hosting.

## Configuration Files
```
config/
  identity.yml
  repos.yml
  redaction.yml
  exclusions.yml
  ai_sources.yml
```
`repos.yml` allows per-repo visibility, e.g.:
```yaml
repos:
  meshic:
    visibility: public
    label: Meshic
    category: Real estate intelligence platform
  private-client-repo:
    visibility: redacted
    label: Data platform build
    category: Private software system
  sensitive-repo:
    visibility: aggregate_only
```

## Methodology Notes (the dashboard must explain)
How repos were discovered; how commits were counted; how user-authored commits were identified; how LOC was calculated; which files/dirs were excluded; how private repos were redacted; how generated/vendor code was handled; how AI evidence was detected; what is measured fact vs inferred indicator.

## Design Requirements
Clean, restrained, numerical, auditable, weekly-updated, public-safe. **Not** over-claiming, **not** employer-branded, **not** framed as a CV.
Avoid: "AI wizard" language; fake productivity multipliers; unverifiable token estimates; inflated LOC; exposing private repo data; raw private commit messages; vanity metrics without context.

## Final Standard (user's stated bar)
> What has been built, how much engineering activity has occurred, how substantial was it, and what evidence supports that conclusion?
Make raedmund.com function as a **live proof-of-work ledger**, not a static personal website.

## Design Reference (user-provided, 2026-06-24)

Raedmund shared a sample dashboard mockup (`reference-dashboard-mockup.pdf`, copied into this workspace) as the intended look and feel — "something along these lines."

**Visual language (observed):** restrained, numerical, light theme; monospace labels (caps, letter-spaced) + large clean numerals; muted blue accent; GitHub-style daily-commit-intensity heatmap; commits/month and LOC/month bar charts; card-grid layout.

**Integrity cues (strong — keep these):**
- "SAMPLE DATA — Representative figures shaped to the `build-ledger.json` schema. Replace with collector output to go live." (signals auto-generation + the data contract)
- Tagline: "A continuously-updated, inspectable record of engineering activity across all accessible repositories. A proof-of-work ledger — measured, auditable, not a CV."

**Hero metrics shown:** Repositories analysed (47; public/private/archived) · Total commits (9,612; user-authored, active days) · Net LOC (363.5k; added/removed). Sub-cards: active/archived repos, files touched, languages, test files, CI/CD workflows, DB migrations, docs/ADRs (+ at least one column clipped).

**Open positioning question (raised, not yet decided):** the hero leads with *volume* (repos/commits/LOC), which is in tension with the brief's *provenance-first* decision. AI-native-evidence placement is not visible in the shared capture (right column and lower sections are clipped). To resolve at the brief/UX level: provenance-first vs. comprehensive-ledger emphasis (comprehensive data can be kept with provenance-forward presentation).

## Design & Metrics Direction — Critique Round 2 (user, 2026-06-24)

User's own critique of the mockup. **Verdict:** strong concept, but it "still leans too much on volume" and reads like "a polished résumé dashboard pretending not to be a résumé." Direction: fewer big numbers, more **inspectable evidence of engineering judgement** — auditability, system maturity, architectural evidence, weekly freshness, privacy-preserving verification, and AI-native workflow infrastructure. _(This critique resolves the open positioning question above: decisively evidence-system / provenance-first.)_ Most items below are UX/PRD-level detail parked here; the brief absorbs only the framing shifts.

1. **Credibility layer.** Drop bare "SAMPLE DATA" (undermines everything). Dataset trust modes: **Live verified** (repo collectors) / **Redacted verified** (real private data, privacy-protected) / **Demo/sample** (representative). Per-figure badges: `Measured` / `Inferred` / `Redacted` / `Sample` / `Excluded`. Turns claims into an evidence system.
2. **Split vanity vs capability metrics.** Commits/LOC are blunt and can look like padding. Add higher-signal: repos-with-tests / -CI / -migrations / -prod-like-deploy; median repo lifespan; longest sustained streak; % commits on still-active systems; (docs+specs+tests):source ratio; refactor/maintenance share; bugfix vs feature vs infra commits; # ADRs; # domain models / APIs / pipelines / scheduled jobs. Proves maturity, not keyboard activity.
3. **"What this proves" interpretation layer.** Explicit, e.g.: sustained solo output over years; breadth (backend/frontend/GIS/data/AI tooling/deploy); non-toy systems (migrations/tests/CI/jobs/APIs/pipelines); LLM-native workflows *augmenting* architecture, not replacing it; privacy-preserving public evidence.
4. **Drill-down evidence packs** (page = executive index → linked depth): Engineering Ledger Summary (public dashboard) · Repository Evidence Pack (per-repo, redacted) · Architecture Evidence Pack (ADRs, migrations, service boundaries) · AI-Native Development Pack (agent files, evals, MCP, prompts) · Data Systems Pack (pipelines, schedulers, geo/ingest) · Hiring/Client Pack (clean PDF for non-technical readers).
5. **De-fluff AI evidence** (vulnerable to "theatre"). Three buckets: **Workflow infrastructure** (MCP tools, agent instruction files, eval harnesses, model config, orchestration code) · **Delivery artefacts** (implementation plans, session logs, PR reviews, task plans) · **Quality controls** (eval tests, architecture guards, CI checks, prompt regression cases). Shows a *system around the models*, not chatting.
6. **Momentum & decay** (trajectory): windows last 7d / 30d / 90d / trailing 12m / previous-12m comparison; per window: commits, LOC touched, active repos, tests added, docs/specs. Makes it feel alive.
7. **"Excluded from counts" — make prominent** (inoculates vs LOC-inflation): forks, vendored deps, generated artefacts, lockfiles, minified, abandoned experiments, dependency churn, bot-authored commits, duplicated mirrors.
8. **Rework repo table** (too flat). Add columns proving system quality: Tests, CI, Migrations, Docs/ADRs, Deployable?, AI tooling?, Domain complexity. (Single "Complexity" column too compressed.)
9. **"Representative systems" section** (named systems > numbers): Meshic (retail real-estate intelligence — PostGIS, ingestion pipelines, canonical entity resolution, co-tenancy scoring, portfolio analysis); geo-ingest (scheduled geospatial ingestion — source normalisation, spatial joins, reproducible runs); mcp-toolbelt (MCP tooling layer — tool defs, eval harnesses, agent instructions).
10. **Visual hierarchy** (reads like a stats dump). Suggested order: Hero claim → Freshness (last/next run, collector version) → Trust status → Top proof metrics (active repos, user commits, active days, tests, CI, migrations) → What this proves → Activity over time → Representative systems → Repo table → Language/stack → Complexity signals → AI-native evidence → Methodology/privacy → Download/export.
11. **Collector transparency / ledger metadata:** collector version, GitHub identities included, date range, excluded paths, LOC tool, schema version, dashboard commit hash, link to `build-ledger.json`, checksum of public export. (Difference between "portfolio page" and "audit artefact".)
12. **Private verification route:** redacted evidence bundle on request for selected reviewers (per-repo collection logs, commit-attribution summary, test/CI evidence, architecture artefact index, redacted file-tree summaries). Stronger than exposing everything publicly.
13. **Soften self-awardy superlatives:** "Largest *measured* codebase," "Most active *by user-authored commits*," "Highest *structural-complexity score*," "Highest *AI-workflow evidence count*." More boring, more credible.
14. **Transparent complexity score** (avoid vague labels): weighted dimensions — API/service 15, DB/migrations 15, tests 15, CI/CD 10, data pipelines 15, deployment 10, docs/ADRs 10, AI tooling/evals 10; each repo gets a visible score. _[Facilitator watch-out: a self-chosen weighting is still an opinion a skeptic can discount. Consider inspectable raw signals + reader-judges, or label the score explicitly as opinion. Decide in PRD.]_
15. **Best single line** (near top): *"This is not a productivity score. It is an evidence ledger showing sustained, inspectable engineering activity across real repositories: code, tests, CI, migrations, data pipelines, documentation, architecture decisions and AI-native development artefacts."*

**Also surfaced:** candidate representative repos now named — **Meshic, geo-ingest, mcp-toolbelt** (confirm/expand).

## Consolidated v1 Module Scope, Data Sources & Invariants (post brainstorm + recon, 2026-06-24)

**Purpose dimension added:** Build Ledger is dual-purpose — an external **window** (GL proof) plus a personal **mirror** (self-insight). Central insight: it is the same artifact; build for the mirror and the window follows (self-directed honesty is unfakeable).

**Recon reality (GitHub `Pinstack`, scanned 2026-06-24):** 47 owned repos (12 public / 35 private / 0 forks), Python-dominant, 2025–26 ramp; AI-native artefacts real (AGENTS.md ×9, CLAUDE.md, .cursorrules; **22 repos with `.claude/`**); 8 CI, 16 tests, 11 migrations. Flagship **Meshic** = 5,511 files / 1,434 commits; **commit authors = Raedmund (1,390) + cursor[bot] (45) + Cursor Agent (1) + dependabot (59)**. Raedmund is **fully AI-native** (no traditional coding background). Local agentic logs: ~/.claude/projects (1,286 sessions) + ~/.codex (1,663 sessions); sampled Claude **cache-hit ratio ~91%**, deliberate model routing (Opus/Sonnet/Haiku).

**v1 modules + data sources:**
1. **Repo / metrics** — GitHub GraphQL/REST (authed as `Pinstack`) + local clones.
2. **Git co-authorship (HERO)** — parse commit authors + `Co-authored-by:` trailers → human/agent split per repo. Un-fakeable agentic proof.
3. **AI-native artefacts** — detect `CLAUDE.md`/`AGENTS.md`/`.cursorrules`/`.claude`/`mcp(.json)`; classify into workflow-infra / delivery-artefacts / quality-controls.
4. **Agentic practice & efficiency** — local Claude Code and Codex logs, **aggregate-only** (scripted; never load or publish transcripts): session cadence, model mix, cache-hit ratio, honest cost totals (pricing source labelled), and cost trend over time (confounders noted). Framed as efficiency-as-craft, not spend; primarily a mirror signal.
5. **Retrospective** — sourced from BMAD memlogs (planning) + git (coding); the meta "building Build Ledger" retro is available and self-evidencing. Mirror = brutally honest; window = curated/confident.
6. **In-flight** — auditable only: WIP branches, open issues, draft PRs, TODO/FIXME counts, commit trajectory. Never aspirational.
7. **Safe-by-default redaction** — private repos → silhouettes (shape + signals, no names/paths/messages); allowlist for exceptions.

**Closed loop:** modules feed `build-ledger.json` → page → retrospective → informs next build (the "OS for your engineering").

**Invariants to lock in the PRD (the reason for PRD-before-build):**
- **`build-ledger.json` schema** — the collector↔page contract; every module feeds it.
- **Redaction / privacy rules** — safety-critical over 35 real private *client* repos; written + reviewed before any private clone.
- **v1 module emit-specs** + the explicit v1-vs-Vision cut.

**Cursor note:** local Cursor data (~15 GB `state.vscdb`) is messy for token extraction — rely on git co-authorship as the clean Cursor signal. Cloud dashboards (claude.ai / platform.openai.com) need an export or API key — out of scope for v1.

## Cross-provider AI-attribution research (architecture/build feeder, 2026-06-24)

**Why this section exists.** v1's hero metric is the commit-level Co-Authorship Split from git `Co-authored-by:` trailers — **~61.4% of commits AI-co-authored**. That figure is a **lower bound**, not the achievement: trailers are the *weakest* attribution method (lots of AI code was hand-committed with no trailer). This section captures the landscape researched for recovering the *true*, higher-coverage **line-level** picture, ranked for a **solo / local / privacy-preserving** builder, plus what was deliberately rejected. It feeds architecture (the v1.5 line-level phase and the Vision store), not v1 build. Maps to PRD FR-3 (commit-level floor), FR-13 (line-level, v1.5), FR-5 (Acceptance Ratio), §6.1.1 (v1.5), §6.2 (Vision), and the forward-compatible `attribution` schema.

### The four Attribution Layers (ranked: coverage impact × solo/local/privacy feasibility)

| # | Layer | Unit | What it gives | Feasibility (solo/local) | PRD phase |
| --- | --- | --- | --- | --- | --- |
| 1 | **Session-diff reconciliation** *(standout)* | line | Parse the builder's existing local Claude Code (`~/.claude`, ~1,286 sessions) + Codex (`~/.codex`, ~1,663 sessions) logs; match AI edit/diff events to commits → **line-level** AI attribution, **backfilled across all history**. | **HIGH** — data is already on disk; aggregate-only; no network, no admin. | **v1.5** (FR-13) |
| 2 | **git-notes attribution store** (`refs/notes/ai`) | line | Provenance that travels *with* the repo, survives rebase/squash, independently verifiable. The auditable *format* for line-level attribution. | HIGH — local git; adds a notes ref. | **Vision** |
| 3 | **Claude Code OpenTelemetry** (`code_edit_tool_decision`) | line (offered/kept) | An **acceptance ratio** = AI lines *offered vs. kept*. A denominator-aware *quality/efficiency* signal, going-forward, via a local OTLP collector. | MEDIUM — needs a standing local collector; going-forward only (no backfill). | v1.5 reads the ratio (FR-5); standing collector is **Vision** |
| 4 | **Diff heuristics** | line | Low-confidence fallback to bound the *unattributed remainder*; label results **"inferred"**. | HIGH but low-confidence — never merged into measured figures. | **v1.5** as the labelled remainder under `attribution` |

**Layer ranking rationale:** Layer 1 is the standout because it converts the commit-level lower bound into a true line-level measure using data the builder *already has locally*, with no admin gate and no transcript exposure (aggregates only). Layers 2–3 strengthen auditability and quality framing but are later. Layer 4 only bounds what the others miss.

### Out of scope (and why)

- **Cursor / Copilot acceptance APIs** — their acceptance/usage telemetry is **org/team-admin-gated**, not available to a **solo** user. So Cursor's clean signal stays the commit-level Co-Authorship Split, and line-level coverage comes from the local Claude Code/Codex logs (Layer 1). Excluded in **all** versions.
- **Cloud dashboards** (claude.ai / platform.openai.com) — need export/API key (already noted above).

### Tools surveyed

`ccusage`, `agentblame`, **Git AI** (usegitai), **origin-cli** (history backfill), `diffity`, `claude-code-otel`. Surveyed for method, not adopted wholesale.

### Adopt (anti-vanity-filtered)

- **Acceptance Ratio** as the quality signal that **beats token counts** — offered vs. kept (Layer 3 method, surfaced in PRD FR-5 / SM-6). It is the **honesty guard**: for a fully AI-native builder the line-level AI % is high by construction, so "how much was kept" keeps the story *judgment*, not *volume*.
- **git-notes attribution store** (`refs/notes/ai`) as the line-level evidence *format* (Vision).
- **Retroactive backfill** of line-level attribution across all history (Layer 1).
- **Line → model → session backlink** (drill-to-proof): a line-level figure can be traced to the model and session that produced it — the line-level analogue of the commit-level "drill from claim to git evidence" journey. (Aggregates/counts only on the public surface; the backlink proof is a local/Mirror capability — never exposes transcripts; ties to Redaction Rules.)

### Reject explicitly (vanity patterns)

- **Cost/token leaderboards** of any kind.
- **"Wrapped"-style spend flexing** (year-in-review spend recap).
- **Desk-toy spend counters** (a live ticking dollar/token meter).

These map to PRD §5 Non-Goals and counter-metric SM-C1. The whole point of adopting the Acceptance Ratio is to have a quality signal that does *not* reduce to spend.

### Forward-compatible schema note

Line-level results land in the PRD's optional multi-layer **`attribution`** representation (`method`, `unit = commit|line`, `confidence = measured|inferred`, `source`, plus `ai_lines`/`total_lines`/`acceptance_ratio`) under a **`schema_version` MINOR bump (→ `1.1.0`)** — additive only, so the v1 commit-level `coauthorship` shape (tagged `unit: "commit"`) is untouched and v1 pages keep rendering. Aggregate counts/ratios only; **no transcript or session-log text** ever enters the public file (Redaction Rules / FR-5 / FR-6).
