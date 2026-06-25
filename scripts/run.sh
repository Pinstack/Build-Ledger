#!/usr/bin/env bash
# Fast-track (FR-7, Story 3.6): one command produces a publishable cut.
#   collector run -> validate (schema + fail-closed redaction) -> static site build.
# Local-primary (AD-1): the live collector needs `gh` + ~/Projects clones on a trusted machine.
#
# Toolchain (auto-resolved below): contract.py uses 3.10+ runtime annotations, and Astro 6
# hard-refuses Node < 22.12. A bare `python3`/`node` is often older (macOS ships Python 3.9; a
# stale nvm default can be Node 20), so the unattended weekly schedule must NOT lean on shell
# defaults — we pin compatible runtimes here. Override with PYTHON=... / NODE_BIN=... ; `.nvmrc`
# pins the Node version for `nvm use`.
#
# Usage: scripts/run.sh [live|seed]
#   live  (default) — recompute everything from source (trusted local machine)
#   seed            — converge the committed snapshot into the v1 contract (no clones needed)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-live}"
cd "$ROOT"

# --- Resolve a Python >=3.10 that also has the one runtime dep (PyYAML) ---
resolve_python() {
  local c found=""
  for c in "${PYTHON:-}" python3.13 python3.12 python3.11 python3.10 python3; do
    [ -n "$c" ] || continue
    command -v "$c" >/dev/null 2>&1 || continue
    "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)' 2>/dev/null || continue
    found="$c"
    "$c" -c 'import yaml' 2>/dev/null && { command -v "$c"; return 0; }
  done
  if [ -n "$found" ]; then
    echo "ERROR: $("$found" -V 2>&1) meets the >=3.10 floor but PyYAML is missing — run: $found -m pip install -r collector/requirements.txt" >&2
  else
    echo "ERROR: no Python >=3.10 found (have $(python3 -V 2>&1 || echo none)) — install 3.10+ or set PYTHON=/path/to/python" >&2
  fi
  return 1
}

# --- Put a Node >=22.12 on PATH for the Astro build ---
node_ok() {
  local n="${1:-node}"
  command -v "$n" >/dev/null 2>&1 || return 1
  "$n" -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit((a>22||(a===22&&b>=12))?0:1)' 2>/dev/null
}
ensure_node() {
  if [ -n "${NODE_BIN:-}" ] && node_ok "$NODE_BIN"; then export PATH="$(dirname "$NODE_BIN"):$PATH"; return 0; fi
  node_ok node && return 0
  local nvm_sh="${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  if [ -s "$nvm_sh" ]; then
    set +eu; . "$nvm_sh"; nvm use >/dev/null 2>&1 || nvm use --lts >/dev/null 2>&1 || true; set -eu
    node_ok node && return 0
  fi
  local v
  for v in 24 26 25 22; do
    if node_ok "/opt/homebrew/opt/node@$v/bin/node"; then export PATH="/opt/homebrew/opt/node@$v/bin:$PATH"; return 0; fi
  done
  echo "ERROR: need Node >=22.12 for the Astro build (have $(node -v 2>&1 || echo none)) — install Node 22+ (\`nvm install\`), or set NODE_BIN=/path/to/node" >&2
  return 1
}

PY="$(resolve_python)" || exit 1
echo "==> Python: $("$PY" -V 2>&1)  ($PY)"

echo "==> Collector ($MODE)"
if [ "$MODE" = "seed" ]; then
  "$PY" collector/seed.py
else
  "$PY" collector/collect.py
fi

echo "==> Validate (schema + whole-document redaction, fail-closed)"
"$PY" collector/validate.py public/build-ledger.json --redaction

echo "==> Build static site"
ensure_node || exit 1
echo "==> Node: $(node -v)  ($(command -v node))"
cd site
[ -d node_modules ] || npm ci
npm run build   # runs sync-ledger -> astro build -> verify-build (postbuild gate)

echo "==> Publishable cut ready in site/dist/  (deploy: scripts/deploy.sh)"
