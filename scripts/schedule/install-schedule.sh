#!/usr/bin/env bash
# Install the weekly launchd schedule on macOS (AD-1: local-primary). For Linux, use cron — see
# crontab.example in this directory.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLIST_SRC="$ROOT/scripts/schedule/com.raedmund.build-ledger.plist"
DEST="$HOME/Library/LaunchAgents/com.raedmund.build-ledger.plist"

if [ "$(uname)" != "Darwin" ]; then
  echo "Not macOS. Use cron instead — see $ROOT/scripts/schedule/crontab.example"
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.build-ledger/private"
sed "s#__ROOT__#$ROOT#g; s#__HOME__#$HOME#g" "$PLIST_SRC" > "$DEST"
launchctl unload "$DEST" 2>/dev/null || true
launchctl load "$DEST"
echo "Loaded weekly schedule: $DEST"
echo "It runs scripts/scheduled-run.sh every Monday 09:00 (run -> validate -> build -> deploy)."
