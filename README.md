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

From [`public/build-ledger.json`](public/build-ledger.json) (generated 2026-06-24, collector `v0.2.0`):

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
collector/collect.py     # the collector (v0.2.0 spike) — GitHub + local clones -> JSON
public/build-ledger.json # the generated, redaction-safe public artifact
_bmad-output/            # v1 planning: brief, PRD, architecture spine, SPEC, epics & stories
```

## Running the collector

Requires the [GitHub CLI](https://cli.github.com/) authenticated, and local clones under `~/Projects` for the commit-level signals:

```bash
python3 collector/collect.py
# -> writes public/build-ledger.json
```

It reads the repo list via `gh`, computes co-authorship and signals from local clones where present, aggregates, runs the redaction safety gate, and writes the ledger.

## Status

v1 is fully planned (brief → PRD → architecture spine → SPEC → epics & stories, all under `_bmad-output/`); the collector is an early spike. The `agentic_practice`, `retrospective`, and `in_flight` sections of the schema are stubbed for the next iteration.

---

*Note on privacy: client names in the planning documents have been anonymized (`Client A` / `Client B`). Private repositories appear only as aggregate silhouettes, by design.*
