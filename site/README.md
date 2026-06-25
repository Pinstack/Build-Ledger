# Site

The Generated Page — a build-time static Astro render of `build-ledger.json` at the Route
`raedmund.com/engineering` (AD-8). No runtime fetch, no charting library, no client JS: every figure
is in view-source, charts are server-generated inline SVG.

## Build

Requires **Node ≥22.12** (Astro 6 refuses anything older) — see [`../.nvmrc`](../.nvmrc): `nvm use`.

```bash
cd site
npm install
npm run build      # sync-ledger -> astro build -> verify-build (FR-10 gate)
npm run preview    # serve dist/ locally
```

`npm run build` first copies the canonical, redacted `../public/build-ledger.json` into `src/data/`
(imported and rendered) and `public/` (served beside the page so a reader can diff page-vs-file),
then builds, then runs `scripts/verify-build.mjs` — which fails the build if the page isn't static,
loses the provenance hero, or drops the audit links.

## What it renders

Provenance-first order: the **Co-Authorship Split** hero (AI-co-authored share as an explicit lower
bound, with a drill-to-evidence per-author breakdown that reconciles to the headline) and the
classified **AI-Native Artefacts** lead; repos/commits/LOC are supporting cast; the repository ledger
shows public repos in full and private ones as Silhouettes (opaque id, no name); Methodology and
Excluded-from-counts notes close it. Mirror sections (practice / retrospective / in-flight) and the
activity charts render an intentional "no data this run" state until their data is present.

The page reads `schema_version` first and **refuses an unsupported MAJOR** rather than mis-render (AD-7).

## Deploy ($0, pre-built)

```bash
scripts/run.sh live          # or: scripts/run.sh seed   (collector -> validate -> build)
scripts/deploy.sh            # wrangler pages deploy site/dist  (Cloudflare Pages free tier)
```

No host build, no GitHub Actions; the host is swappable (any static host serves `dist/`). The weekly
refresh is a local scheduler — `scripts/schedule/install-schedule.sh` (launchd) or `crontab.example`.
