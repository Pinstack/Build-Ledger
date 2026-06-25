# Build Ledger

**An auditable proof-of-work ledger for AI-native engineering — a window for others, a mirror for you.**

Build Ledger is a public, inspectable record of *how* software gets built with AI agents — generated from real repositories, not hand-authored. It turns the usually-invisible evidence of agentic work — agent instruction files, MCP tooling, orchestration code, and the git history itself — into something a skeptic can open and verify. It is an **evidence ledger, not a productivity score**.

## The hero signal: git co-authorship

The headline metric is the **human vs. AI-agent commit split**, read straight from commit metadata:

- **Trailer-based (primary):** commits carrying a `Co-authored-by: <AI model>` trailer — the human commits, the model is credited, the exact model is named per commit. Auditable provenance that can't be back-filled.
- **Author-based (secondary):** commits an agent identity authored autonomously (e.g. `cursor[bot]`).
- **Bot noise** (dependabot, renovate, CI, semantic-release) is classified *out* of the headline — counted, but never sold as agent work.

## Safe-by-default redaction

The collector is built privacy-first, and the rule is enforced centrally with a hard assertion before write:

- **Public repos** — named, in full detail.
- **Private repos** — **silhouettes**: shape and signals only (`Private project N`), with no name, path, commit message, or per-model breakdown.
- The **Allowlist** is the only mechanism that promotes a private repo above a silhouette. **v1 ships with an empty Allowlist** — every private repo stays a silhouette.

A `SAFETY GATE` in [`collector/collect.py`](collector/collect.py) asserts that no private record ever carries an identifying field; the build fails loudly if it would.

## Snapshot

From [`public/build-ledger.json`](public/build-ledger.json) (`schema_version 1.0.0`, collector `v1.0.0`, data collected 2026-06-24):

| | |
|---|---|
| Repositories | 47 (12 public · 35 private silhouettes) |
| Total commits | 2,080 |
| AI-co-authored | 1,277 (**61.4%**) |
| Agent-authored (autonomous) | 46 |
| Bot noise excluded | 62 |
| Repos with tests / CI / migrations | 9 / 7 / 3 |
| Top languages | Python, HTML, TypeScript, JavaScript |

## Layout

```
collector/               # the local-primary Collector (v1) — discover -> redact -> emit
  collect.py             #   assembler & entrypoint (tiering, id-keyed merge, atomic publish)
  contract.py            #   the build-ledger.json contract: schema, enums, validator
  redaction.py           #   central fail-closed whole-document redaction (SAFETY-CRITICAL)
  modules/               #   one file per Module (repos, coauthorship, artefacts, …)
  config/                #   reviewable YAML (identity, repos, redaction, exclusions, …)
  tests/                 #   zero-dependency unittest suite (proves the invariants)
public/build-ledger.json # the generated, redaction-safe public artifact (the one contract)
site/                    # Astro 6 static page at /engineering, rendered from the file (Epic 3)
_bmad-output/            # v1 planning: brief, PRD, architecture spine, SPEC, epics & stories
BUILD-LOG.md             # autonomous build progress, story-by-story
```

## Running the collector

Requires the [GitHub CLI](https://cli.github.com/) authenticated, and local clones under `~/Projects` for the commit-level signals:

```bash
python3 collector/collect.py
# -> writes public/build-ledger.json
```

It reads the repo list via `gh`, computes co-authorship and signals from local clones where present, aggregates, runs the redaction safety gate, and writes the ledger.

## Status

v1 is fully planned (brief → PRD → architecture spine → SPEC → epics & stories, all under `_bmad-output/`) and the build is underway, story-by-story (see [`BUILD-LOG.md`](BUILD-LOG.md)):

- **Epic 1 (redaction-safe evidence file) — done.** Versioned contract + validator, the central fail-closed whole-document redaction gate, the assembler (tiering → id-keyed merge → derived aggregates → atomic publish), and base repo metrics. 63 passing tests prove the safety-critical invariants over fixtures.
- **Epic 2 (the hero) — done.** Commit-level Co-Authorship Split (named agents, bots distinguished, share stated as an explicit lower bound) and three-class AI-Native Artefact classification.
- **Epic 3 (the published page) — next.** The Astro `/engineering` page rendered from the file.
- **Epic 4 (the Mirror) — pending.** `agentic_practice`, `retrospective.window_view`, and `in_flight` currently render as typed-empty (`available: false`) until their Modules land.

The Collector is *local-primary* (AD-1): the live scan of real repositories runs on the trusted local machine; the committed artifact above is the builder's real prior collection converged into the v1 contract through the same redaction-gated pipeline.

---

*Note on privacy: client names in the planning documents have been anonymized (`Client A` / `Client B`). Private repositories appear only as aggregate silhouettes, by design.*
