#!/usr/bin/env bash
# Fast-track (FR-7, Story 3.6): one command produces a publishable cut.
#   collector run -> validate (schema + fail-closed redaction) -> static site build.
# Local-primary (AD-1): the live collector needs `gh` + ~/Projects clones on a trusted machine.
#
# Usage: scripts/run.sh [live|seed]
#   live  (default) — recompute everything from source (trusted local machine)
#   seed            — converge the committed snapshot into the v1 contract (no clones needed)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-live}"
cd "$ROOT"

echo "==> Collector ($MODE)"
if [ "$MODE" = "seed" ]; then
  python3 collector/seed.py
else
  python3 collector/collect.py
fi

echo "==> Validate (schema + whole-document redaction, fail-closed)"
python3 collector/validate.py public/build-ledger.json --redaction

echo "==> Build static site"
cd site
[ -d node_modules ] || npm ci
npm run build   # runs sync-ledger -> astro build -> verify-build (postbuild gate)

echo "==> Publishable cut ready in site/dist/  (deploy: scripts/deploy.sh)"
