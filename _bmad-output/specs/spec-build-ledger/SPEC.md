---
id: SPEC-build-ledger
companions:
  - ../../planning-artifacts/prds/prd-Build-Ledger-2026-06-24/prd.md
  - ../../planning-artifacts/architecture/architecture-Build-Ledger-2026-06-25/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/briefs/brief-Build-Ledger-2026-06-24/addendum.md
sources:
  - ../../planning-artifacts/briefs/brief-Build-Ledger-2026-06-24/brief.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. The **PRD** companion holds each capability's detailed testable consequences, the user journeys, the full `build-ledger.json` API contract, and the Glossary (downstream MUST use its terms verbatim). The **architecture spine** companion holds the 15 binding `AD`s (ids stable). The **addendum** holds the `config/*.yml` layout, code-exclusion lists, and the four Attribution Layers. Capability IDs here (`CAP-N`) carry their originating `FR-N` for traceability.

# Build Ledger

## Why

A **vision to realize**, with a live **mandate** behind it. Build Ledger is a public, inspectable record of *how* an AI-native engineer builds software with agents — generated from real repositories, refreshed weekly, never hand-authored — so that the usually-invisible evidence of agentic work (co-authorship metadata, agent instruction files, orchestration, evals, shipped systems) becomes something a skeptic can open and verify. It serves two readers who are the **same artifact**: the **Window** (the GL *FDE — Agentic Solutions* hiring evaluator, agentic-native, hype-allergic, grades taste) and the **Mirror** (the builder himself, asking "am I growing or just busy?"). Build for the Mirror and the Window comes free, because self-directed honesty cannot be faked. It matters now because of an acute **AI-credibility gap** — adoption is high, trust is falling, "vibe coding" reads as a red flag — and because the builder is **fully AI-native** with no seniority fallback, so the work must speak entirely through auditable evidence. The artifact demonstrates the very skill it documents.

## Capabilities

- **CAP-1 — Metrics computed from source, volume subordinate to provenance** *(FR-1, FR-2)*
  - **intent:** Discover the subject's repositories (authenticating as Pinstack) and compute conventional metrics — repo counts, commits, active days, LOC, languages, test/CI/migration presence — from source, applying the Excluded-from-counts list before any figure, and present them below provenance.
  - **success:** Every numeric figure on the page traces to a Collector-emitted value in `build-ledger.json` (none hand-entered); the exclusions are itemized on the page; the hero region leads with provenance, not volume.

- **CAP-2 — Commit-level Co-Authorship Split (HERO), stated as a lower bound** *(FR-3)*
  - **intent:** Per repository, compute the human/agent commit split from commit authors plus `Co-authored-by:` trailers, naming each agent author, and present the AI-co-authored share as an explicit **commit-level lower bound**.
  - **success:** For a repo with known co-authors the split names each agent (e.g. `cursor[bot]`, `Cursor Agent`) with counts; the headline is labelled a commit-level lower bound with the Methodology explaining why; per-author evidence is on or linked from the page (counts only, no commit messages).

- **CAP-3 — Detect and classify AI-native artefacts** *(FR-4)*
  - **intent:** Detect AI-native artefacts (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.claude/`, `mcp`/`.mcp.json`) and assign each to exactly one of three Artefact Classes (workflow-infrastructure / delivery-artefacts / quality-controls).
  - **success:** Presence is detected and counted per repo; each artefact appears under exactly one class; private repos surface the aggregate signal only (no path or name).

- **CAP-4 — Aggregate agentic practice without transcripts** *(FR-5)*
  - **intent:** Compute aggregate practice and efficiency (cadence, model mix, cache-hit ratio, honest cost totals, cost trend) from local Claude Code and Codex logs, framed as efficiency-as-craft, never reading or emitting transcript content.
  - **success:** No transcript text appears in the file or on the page; every cost figure carries a labelled pricing source (logged figures, or a pinned `config/pricing.yml` with `as_of`), never estimated; the trend names at least one confounder; it is not rendered as a leaderboard.

- **CAP-5 — Sourced Retrospective in two framings** *(FR-11)*
  - **intent:** Produce a Retrospective from BMAD memlogs + git in two framings — a curated **Window View** that publishes, and a brutally-honest **Mirror View** that is private-only.
  - **success:** Every claim traces to a memlog entry or git evidence; the public file carries `retrospective.window_view` only and has **no** `retrospective.mirror_view` key; the Mirror View exists only in the private mirror artifact.

- **CAP-6 — In-Flight from auditable signals only** *(FR-12)*
  - **intent:** Compute In-Flight from live repository signals (WIP branches, open issues, draft PRs, in-code work-markers, commit trajectory), excluding any aspirational or planned-but-unstarted item.
  - **success:** Every In-Flight item is backed by a live repo signal at run time; private repos surface aggregate-only (no branch or issue names); the section is labelled as live signals with the run timestamp.

- **CAP-7 — Safe-by-default, fail-closed redaction** *(FR-6)*
  - **intent:** Apply the Redaction Rules on every run, defaulting every private repo to `display_tier: aggregate_only`, and assert over the whole public document before publish (fail-closed); the Allowlist (empty in v1) is the only promotion path.
  - **success:** A fixture exercising all five public blocks (including a private repo) produces a published file containing none of the prohibited fields (name / path / branch / commit message / secret / client name / transcript) and no `mirror_view` key; a run that cannot assert clean does not publish.

- **CAP-8 — Single `build-ledger.json` contract** *(FR-8)*
  - **intent:** Emit exactly one `build-ledger.json` per run conforming to the documented shape, carrying `schema_version`, with every Module nested and a no-data Module represented explicitly (`available: false`).
  - **success:** The file validates against the documented top-level shape and `schema_version`; the page renders solely from it; a missing Module is present as `available: false`, not omitted.

- **CAP-9 — Local schedule + on-demand fast-track** *(FR-7)*
  - **intent:** Run the Collector weekly via a local scheduler (`launchd`/cron) and manually on demand, where a single manual run produces a publishable cut before the schedule is enabled.
  - **success:** A manual trigger produces a complete `build-ledger.json` and a rebuilt page without the weekly schedule; scheduled and manual runs emit the same shape; redaction is applied on every run before publish.

- **CAP-10 — Publish the Generated Page with Ledger Metadata + Methodology** *(FR-9)*
  - **intent:** Render a build-time static page at the Route with visible Ledger Metadata, the Methodology Note, and the Excluded-from-counts Note.
  - **success:** The page shows run timestamp, Collector version, `schema_version`, identities, date range, and a link to the published `build-ledger.json`; every headline figure is one interaction from its evidence or the Methodology.

- **CAP-11 — Survive inspection as a work sample** *(FR-10)*
  - **intent:** Present a page a skeptical reader can inspect without finding a fabricated figure or a leak, and without it breaking.
  - **success:** No figure lacks a source in `build-ledger.json` plus a Methodology explanation; the page renders without error on latest stable desktop Chrome / Safari / Firefox; attempts to find private internals surface only Silhouettes.

## Constraints

*The architecture spine companion holds the enforceable detail; each constraint cites the binding `AD`.*

- **Local-primary runtime** *(AD-1)* — the Collector runs **only** on a trusted local machine (holding clones, agent logs, memlogs); it is the sole producer of `build-ledger.json` and the private mirror; weekly cadence is a local scheduler, **never** a third-party CI runner. Private repo content/history, agent logs, and the GitHub token never leave the machine; only the redacted `build-ledger.json` does.
- **One coupling, semver contract** *(AD-2, AD-7)* — `build-ledger.json` is the only interface between Collector and Page; the Page renders solely from it; `schema_version` is semver — additive = MINOR (the forward-compatible `attribution` representation for v1.5 line-level), breaking = MAJOR (the Page refuses an unsupported MAJOR).
- **Module ownership + atomic assembly** *(AD-3, AD-13, AD-14, AD-15)* — each Module owns one slice; the assembler (`collect.py`) owns `repositories[]` and the stable `id`s; `aggregates` is a derived projection of the rows; a run builds the whole document in memory then atomic-replaces; pipeline order is tiering → contributions → aggregation → whole-document redaction assert → write; a degraded Module is `available: false`, a fatal error aborts publish; output is deterministic.
- **Fail-closed whole-document redaction** *(AD-4)* — every private repo defaults to `display_tier: aggregate_only`; a single assert runs over the **entire** public document before publish; free-text fields are controlled-vocabulary by construction; the run fails closed if the assert fails; `display_tier` is a fixed three-value enum; the Allowlist is the only promotion path and ships empty in v1.
- **Structural privacy + Mirror never public** *(AD-5, AD-6)* — private outputs (`mirror.json`, raw CSVs) are written **outside** the repo tree, so the one public repo cannot contain private data by construction; the public `retrospective` carries `window_view` only and ships no `mirror_view` key. Safety-critical over ~35 real client repos; rules reviewed before any private clone.
- **Build-time static, free, local deploy** *(AD-8, AD-12)* — the Page is static HTML/CSS/SVG built from the file (no runtime fetch), deployed pre-built to a free static host from local (no GitHub Actions, $0); host is swappable (default Cloudflare Pages). Route = `raedmund.com/engineering`.
- **Aggregate-only telemetry, provenance-first, anti-vanity** *(AD-9, AD-10, AD-11)* — log-derived modules emit counts/ratios only, never transcript text; the hero is co-authorship + AI-native artefacts, with the commit-share a labelled lower bound; the contract carries **no** spend-leaderboard / "Wrapped" / live-counter structure; cost is auditable (pinned, labelled) or omitted, never estimated.

## Non-goals

- **Not a productivity score** — no velocity score, no "10x" multiplier; the page says so.
- **Not a vanity / spend leaderboard** — no token or cost ranking, no "Wrapped"-style spend recap, no desk-toy spend counter, in **any** version.
- **Not employer-branded and not a CV.**
- **Not an aspirational roadmap** — In-Flight shows auditable live signals only.
- **Not a leak surface** — no private repo name, path, branch, commit message, secret, client name, or raw transcript on any v1 path.
- **No dataset trust-modes or per-figure trust badges** — deliberately cut; auditability is structural (generated-from-source + Methodology).
- **Line-level Attribution (FR-13) and the Acceptance Ratio are NOT in v1** — they are v1.5, landing via a non-breaking schema MINOR bump.
- **Cursor / Copilot acceptance APIs are out in all versions** — admin-gated for a solo user.
- **Single-subject only** — no multi-subject generalization or leaderboard breadth (Vision).
- **No complexity-scoring model in v1** — raw inspectable signals instead.

## Success signal

The cold GL DM linking the Generated Page earns a **substantive, human (non-form) reply**. Demonstrated end-to-end: a skeptical agentic-native reader opens the receipts, finds the methodology holds and nothing over-claims, identifies the AI-provenance in under a minute, and the page survives a "fragile or flawed?" read with no fabricated figure and no leak — while the builder returns to it unprompted, because the Mirror tells him something true about his own work.

## Assumptions

- Local Claude Code and Codex logs are readable on the Collector's machine at run time; if absent, Agentic Practice (CAP-4) degrades to "no data this run" rather than failing the run.
- Mobile is best-effort, not a v1 optimization target; the graded target is latest stable desktop Chrome / Safari / Firefox.

## Open Questions

- **Representative-systems framing** — are Meshic / geo-ingest / mcp-toolbelt surfaced as a named "representative systems" section in v1, or deferred? A page-content/UX decision, not a structural invariant; addable later via a non-breaking schema MINOR bump.
- **Unattended-run failure surfacing** — page staleness is self-evident via Ledger Metadata's run timestamp, but a silently-failed local `launchd`/cron run has no active alert. Resolve at build (a minimal local failure notice vs accepting timestamp-staleness for v1).
