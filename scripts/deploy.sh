#!/usr/bin/env bash
# Pre-built, $0 deploy to a free static host (AD-12). Default: Cloudflare Pages via wrangler.
# No host build minutes, no GitHub Actions. The host is seed/swappable — any static host serves
# site/dist/ identically (Netlify drop, GitHub Pages, S3+CDN, …).
#
# Then commit + push the redacted build-ledger.json so its git history is the provenance trail.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/site/dist"
PROJECT="${CF_PAGES_PROJECT:-build-ledger}"

[ -d "$DIST" ] || { echo "no build at $DIST — run scripts/run.sh first"; exit 1; }

echo "==> Deploying $DIST to Cloudflare Pages project '$PROJECT' (pre-built, \$0)"
npx wrangler pages deploy "$DIST" --project-name "$PROJECT" --commit-dirty=true

echo "==> Committing the published artifact (git history = provenance trail)"
cd "$ROOT"
if ! git diff --quiet -- public/build-ledger.json; then
  git add public/build-ledger.json
  git commit -m "ledger: refresh build-ledger.json ($(date -u +%Y-%m-%dT%H:%MZ))" || true
fi
echo "==> Done. Live at the Route."
