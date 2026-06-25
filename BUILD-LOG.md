# Build Ledger — Autonomous Build Log

Progress ledger for the agentic build of v1, working story-by-story from
`_bmad-output/planning-artifacts/epics.md`. Updated as each slice lands.

**Environment note.** The build runs in a remote container. The live collector is *local-primary*
(AD-1): it needs `gh`, local `~/Projects` clones, and the subject's agent logs — none of which exist
in this container, and none of which *should* (the 35 private client repos must never be cloned onto
a non-trusted machine). So the deliverable here is the **software + the safety-critical invariants
proven over fixtures**, plus the committed `public/build-ledger.json` converged from the builder's
real prior collection through the real v1 pipeline. The live full scan (Story 1.6's "over all real
repositories") is the trusted-local-machine step the code is built and tested for.

## Status

### Epic 1 — A redaction-safe evidence file from real repositories ✅
- [x] **1.1** Project skeleton + out-of-tree private drawer + reviewable config scaffold
      (`collector/config/*.yml`, `.gitignore` privacy boundary, `BUILD_LEDGER_PRIVATE` drawer).
- [x] **1.2** `build-ledger.json` contract + semver `schema_version` + validator
      (`contract.py`, `validate.py`).
- [x] **1.3** Assembler — discovery, stable opaque ids, tiering-first, id-keyed merge (`collect.py`).
- [x] **1.4** Central fail-closed whole-document redaction + atomic publish (`redaction.py`,
      `collect.publish`); synthetic-private-repo fixture across all five blocks proves every leak
      vector caught (`tests/test_redaction.py`).
- [x] **1.5** Base repo metrics + signals + derived aggregates with exclusions (`modules/repos.py`;
      `collect.aggregate` is a pure projection of the rows, AD-14).
- [x] **1.6** End-to-end verification — converged real-data `public/build-ledger.json` is
      schema-valid, redaction-safe, legacy-spike-field-free, and every aggregate reconciles
      (`tests/test_e2e.py`). *Live scan over all real repos = the local-machine run.*

### Epic 2 — Provable agentic authorship (the hero) ✅
- [x] **2.1** Commit-level Co-Authorship Split — `unit: commit`, human/agents/excluded_bots,
      AI-co-authored share as an explicit lower bound; forward-compatible `attribution` reserved
      (not emitted in v1) (`modules/coauthorship.py`).
- [x] **2.2** AI-Native Artefact detection + exactly-one-of-three classification
      (`modules/artefacts.py`).

### Epic 3 — A published, inspectable page (the DM fast-track) ✅
- [x] **3.1** Astro 6 site; `/engineering` renders at build time from the file — fully static
      HTML/CSS/SVG, numbers in view-source, no charting lib, no client JS; refuses unsupported
      MAJOR (`site/src/lib/ledger.ts`, `site/src/pages/engineering.astro`).
- [x] **3.2** Provenance-first layout — hero leads with Co-Authorship Split + AI-Native Artefacts,
      "not a productivity score" near the top, share as explicit lower bound; Ledger Metadata +
      audit notes present (`components/Hero.astro`, `LedgerMeta.astro`).
- [x] **3.3** Visual craft — restrained light theme, monospace caps labels, large numerals, muted
      accent, card grid; commit heatmap + commits/month + net-LOC/month as server-generated inline
      SVG (`lib/charts.ts`); no SAMPLE banner / trust badges; empty modules read as intentional. The
      additive `activity` contract key + `modules/activity.py` supply the chart series (live run).
- [x] **3.4** Methodology + Excluded-from-counts content with real per-run counts (`Methodology.astro`).
- [x] **3.5** Drill-to-evidence (per-author breakdown reconciles to the headline) + survives
      inspection (silhouettes only, no leak); post-build `verify-build.mjs` gate (FR-10).
- [x] **3.6** Fast-track `scripts/run.sh` + pre-built `$0` `scripts/deploy.sh` (wrangler / Cloudflare
      Pages, `site/wrangler.toml`).
- [x] **3.7** Weekly local schedule — launchd plist + installer + `crontab.example`
      (`scripts/schedule/`, `scripts/scheduled-run.sh`).

### Epic 4 — The Mirror (honest self-insight signals) ✅
- [x] **4.1** Agentic Practice & Efficiency (`modules/practice.py`) — cadence, model mix, cache-hit
      ratio from local Claude Code/Codex logs, aggregate-only (never transcript text, AD-9);
      auditable-cost-or-none (AD-11): cost computed only from a pinned `pricing.yml`, else omitted.
      Degrades to `available:false` if logs absent.
- [x] **4.2** Two-framing Retrospective (`modules/retrospective.py`) — source-bound from git commit
      subjects + BMAD memlogs (nothing free-authored). The curated Window View publishes; the
      brutally-honest Mirror View is written ONLY to `~/.build-ledger/private/mirror.json`. The
      public object carries no `mirror_view` key (AD-6, machine-verified live).
- [x] **4.3** In-Flight (`modules/in_flight.py`) — WIP branches, TODO/FIXME markers, commit
      trajectory; aggregate counts only, no branch/issue names (Silhouette-safe, FR-12).

*Live entrypoint (`collect.py main`) verified end-to-end in-container: schema-valid + redaction-safe,
window_view populated from this repo's own commits (the self-evidencing build retro), mirror_view
written to the drawer (40 entries), no mirror_view key in the public file.*

## Verification snapshot (latest)

- Collector test suite: **81 passing** (`unittest`, zero-dependency) — all four epics.
- `public/build-ledger.json`: schema_version `1.0.0`, **valid + redaction-safe**.
- Site: **builds static** (`npm run build`), 2 pages; post-build inspection gate passes (no client
  JS, provenance hero + audit links present, `build-ledger.json` served beside the page).
- Headline (commit-level lower bound): **61.4%** AI-co-authored (1277 / 2080 commits);
  47 repos (12 public + 35 silhouettes); 1,972 user-authored commits; 62 bot commits excluded.
