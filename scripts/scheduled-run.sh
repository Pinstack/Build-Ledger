#!/usr/bin/env bash
# Weekly scheduled cut (FR-7, Story 3.7): the SAME pipeline as a manual run — redaction is applied
# before publish exactly as on a manual run (fail-closed). Logs to the out-of-tree private drawer;
# the page's Ledger Metadata timestamp makes any skipped/failed run self-evident (NFR-4).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${BUILD_LEDGER_PRIVATE:-$HOME/.build-ledger/private}"
mkdir -p "$LOG_DIR"
{
  echo "=== build-ledger scheduled run $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  "$ROOT/scripts/run.sh" live
  "$ROOT/scripts/deploy.sh"
  echo "=== ok ==="
} >> "$LOG_DIR/scheduled.log" 2>&1
