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

### Epic 3 — A published, inspectable page (the DM fast-track) ⏳ next
- [ ] 3.1 Scaffold Astro 6 site; `/engineering` renders at build time from the file.
- [ ] 3.2 Provenance-first layout + Ledger Metadata + audit notes.
- [ ] 3.3 Visual craft — heatmap + commits/LOC bar charts as inline SVG; restrained aesthetic.
- [ ] 3.4 Methodology + Excluded-from-counts content.
- [ ] 3.5 Drill-to-evidence + survives skeptical inspection.
- [ ] 3.6 Manual fast-track run + pre-built $0 deploy.
- [ ] 3.7 Weekly local schedule.

### Epic 4 — The Mirror (honest self-insight signals) ⏳ pending
- [ ] 4.1 Agentic Practice & Efficiency from local logs (aggregate-only, auditable-cost-or-none).
- [ ] 4.2 Two-framing Retrospective — Window publishes, Mirror to the drawer only.
- [ ] 4.3 In-Flight from auditable live signals only.

## Verification snapshot (latest)

- Collector test suite: **63 passing** (`unittest`, zero-dependency).
- `public/build-ledger.json`: schema_version `1.0.0`, **valid + redaction-safe**.
- Headline (commit-level lower bound): **61.4%** AI-co-authored (1277 / 2080 commits);
  47 repos (12 public + 35 silhouettes); 1,972 user-authored commits; 62 bot commits excluded.
