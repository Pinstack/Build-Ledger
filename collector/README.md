# Collector

The local-primary batch pipeline (pipes-and-filters behind a versioned data contract) that computes
the evidence from real repositories, redacts it fail-closed, and emits a single `build-ledger.json`.

> **Runtime (AD-1):** the live collector runs **only** on the trusted local machine — it needs the
> `gh` CLI (authenticated as the subject), local clones under `~/Projects`, and (optionally) `tokei`.
> Private repository contents, agent logs, and the GitHub token never leave the machine; only the
> post-redaction public `build-ledger.json` does.

## Layout

```
collector/
  collect.py        # assembler & entrypoint: discover -> tier -> contribute -> aggregate -> redact -> write
  contract.py       # schema version, enums, typed-empty Module builders, validator (the contract)
  redaction.py      # central fail-closed whole-document redaction assert (SAFETY-CRITICAL)
  validate.py       # CLI: validate a build-ledger.json (+ optional --redaction)
  seed.py           # one-time convergence of the v0.2 real snapshot into the v1 contract
  seed_input.json   # the prior real collection (input to seed.py; already public + redacted)
  modules/
    repos.py        # repositories[].metrics + .signals + exclusion tallies (FR-1)
    coauthorship.py # repositories[].coauthorship — the hero, commit-level (FR-3)
    artefacts.py    # repositories[].ai_artefacts — 3-class classification (FR-4)
    # practice.py / retrospective.py / in_flight.py land in Epic 4
  config/           # reviewable YAML (FR-6): identity, repos, redaction, exclusions, ai_sources, pricing
  tests/            # unittest suite (zero-dependency); proves the safety-critical invariants
```

## Pipeline order (pinned, AD-15)

`discover → TIERING (display_tier + stable id) → per-repo Module contributions →
AGGREGATION (derived projection) → whole-document REDACTION assert → atomic write.`

A degraded Module emits typed-empty data and the run continues (AD-3); a redaction-assert failure or
an unvalidatable document aborts the publish entirely, leaving the previous file intact (fail-closed).

## Privacy model (FR-6, AD-4/5/6)

- Every private repo defaults to `display_tier: aggregate_only` (a **Silhouette** — shape + signals +
  aggregate counts, no name/path/label). The **Allowlist** (`config/repos.yml`) is the only promotion
  path and **ships empty in v1**.
- Free-text-bearing fields are restricted to a **controlled vocabulary** by construction; the
  whole-document assert is the fail-closed backstop.
- The sensitive denylist of real private repo / client names lives **outside the repo tree**
  (`~/.build-ledger/private/redaction-denylist.yml`, see `config/redaction.yml`) — never committed.
- The brutally-honest **Mirror View** is written only to `~/.build-ledger/private/mirror.json`; the
  public file has **no** `retrospective.mirror_view` key.

## Run

```bash
# Live run on the trusted local machine (needs gh + ~/Projects clones):
python3 collector/collect.py            # -> public/build-ledger.json

# Validate any candidate file (schema + optional redaction assert):
python3 collector/validate.py public/build-ledger.json --redaction

# Re-converge the committed artifact from the prior real snapshot (no clones needed):
python3 collector/seed.py

# Tests (zero-dependency, stdlib unittest):
cd collector && python3 -m unittest discover -s tests -p 'test_*.py' -t .
```

Only dependency beyond the stdlib is **PyYAML** (`pip install -r collector/requirements.txt`).

## The committed `public/build-ledger.json`

The published artifact is the builder's **real** prior collection (47 repos, 2,080 commits, 61.4%
AI-co-authored — commit-level lower bound) converged into the v1 contract through the *same*
`assemble()` + `publish()` path the live collector uses, so the whole-document redaction assert
genuinely runs over it. Figures the v0.2 snapshot did not carry (LOC churn, active-day counts,
per-author agent names) are emitted as zeros / generic buckets — never fabricated — and are
populated from source by the live local run.
