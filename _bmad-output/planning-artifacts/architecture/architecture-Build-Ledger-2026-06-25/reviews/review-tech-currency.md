---
review: tech-currency
gate: Reviewer Gate
spine: ARCHITECTURE-SPINE.md
spine_path: _bmad-output/planning-artifacts/architecture/architecture-Build-Ledger-2026-06-25/ARCHITECTURE-SPINE.md
reviewer: tech-currency reviewer
date: 2026-06-25
verdict: MINOR-FLAGS
method: live web search (not training data)
---

# Tech-Currency Review — Build Ledger Architecture Spine

**Verdict: MINOR-FLAGS.** Every named technology in the Stack table and the ADs is real, current, and correctly characterized for mid-2026. All headline version claims (Python 3.14, Astro 6, Node 24 LTS) check out against the live web. One forward-looking flag on Cloudflare Pages (host is in maintenance mode — true today, drifting tomorrow) and two small documentation/precision notes are worth recording. Nothing here blocks v1; the host is explicitly seed/swappable in AD-12, which already absorbs the one real risk.

Scope: the Stack table (spine §Stack, lines 110–120) and every technology named in the ADs (esp. AD-1, AD-8, AD-12) and the Structural Seed diagrams. Each item below was reality-checked against live sources dated late-2025 / 2026, not asserted from training data.

---

## Per-item findings

### 1. Python 3.14 (Collector) — VERIFIED ✅
- **Claim:** Python 3.14 is the Collector runtime.
- **Reality:** Python 3.14.0 was released **2025-10-07** (final/stable, per python.org and PEP 745). The 3.14.x line is on **3.14.6** as of mid-2026 — a maintained stable series, well past .0. This is the current production Python at authoring time.
- **Characterization:** Correct. 3.14 is a real, stable, current release — not a pre-release. Targeting `3.14` (not a pinned patch) is appropriate for seed-level guidance; the spine explicitly says "the code owns this once it exists."
- **Verdict:** Current and correctly characterized. No action.

### 2. `gh` CLI (GitHub auth + repo discovery) — VERIFIED ✅
- **Claim:** "current"; used for GitHub auth + repo discovery; local-only token (AD-1, Consistency Conventions "Auth").
- **Reality:** GitHub CLI is actively maintained and remains the canonical first-party tool for `gh auth`, `gh repo list`, and token-scoped local auth. No replacement, rename, or deprecation. Listed as a version-less "current" tool, which is the right call for a CLI the project will pin at install.
- **Verdict:** Current and correctly characterized. No action.

### 3. `git` (history / co-authorship) — VERIFIED ✅
- **Claim:** "current"; source of commit history and `Co-Authored-By` trailer parsing (the co-authorship hero, FR-3).
- **Reality:** git is the universal VCS; `Co-Authored-By:` trailers are a stable, long-standing convention that the co-authorship Module depends on. No currency risk.
- **Verdict:** Current and correctly characterized. No action.

### 4. `tokei` (LOC + language breakdown) — VERIFIED ✅ (with an optional note)
- **Claim:** "current"; LOC + language breakdown tool.
- **Reality:** `tokei` (XAMPPRocky/tokei) is **actively maintained** — recent releases include **13.0.0 (2025-11-25)** and **14.0.0 (2025-12-30)**. It is fast, gitignore-aware, supports 150+ languages, and is a reasonable, current choice for LOC + language counting. The earlier "is tokei abandoned?" era (a long gap around 2021–2022) is over; the 13.x/14.x cadence shows the project is healthy again.
- **scc cross-check (per review brief):** `scc` (boyter/scc, Go) is the main alternative and is also excellent — it adds COCOMO cost estimation and complexity counts, and is comparably/more fast on very large trees. tokei is typically faster on small-to-mid codebases. For ~35 repos either tool is fine. **Optional note, not a defect:** since AD-10 deliberately keeps LOC as "structurally supporting cast, never the lead figure," tokei's simpler output is arguably a better fit than scc's cost/complexity extras (which the spine explicitly rejects a complexity-scoring model in §Deferred). Recommend recording `scc` as a one-line swappable alternative in the build punch-list, mirroring how the host is called swappable — but tokei as the seed default is correct and current.
- **Verdict:** Current and correctly characterized. Optional: note scc as the swappable alternative.

### 5. Astro 6 (site / renderer) — VERIFIED ✅
- **Claim:** Astro 6 is the site renderer; build-time static render to `dist/` (AD-8).
- **Reality:** **Astro 6.0 is real and current** — stable release **2026-03-10** (beta 2026-01-13), per astro.build and docs.astro.build's "Upgrade to Astro v6" guide. It is the latest major line as of mid-2026. So "Astro 6" is not aspirational; it shipped ~3.5 months before authoring.
- **Fit for role:** Strongly correct. Astro's core model *is* build-time static HTML with opt-in islands — exactly what AD-8 specifies ("static HTML/CSS/SVG … islands only where genuinely interactive"). Astro 6 also ships a first-party **Fonts API** and **CSP API**, both relevant to a polished, no-extra-deps static page. Inline server-generated SVG charts (AD-8, "no charting library") is fully supported.
- **Verdict:** Current and correctly characterized. No action.

### 6. Node.js 24 LTS (Astro build) — VERIFIED ✅
- **Claim:** Node.js **24 LTS** as the Astro build runtime.
- **Reality:** Node **24.x is in Active LTS** (2025-05-06 → maintenance through 2028-04-30) and is the **correct LTS to target in June 2026**. Node **26** went *Current* on 2026-05-05 but does **not** enter LTS until **October 2026** — so as of the 2026-06-25 authoring date, 26 is explicitly *not yet* the LTS to target. **The spine picked the right line:** 24 is the newest Active-LTS, and Astro 6 requires a modern Node (18.20.8+/20.3+/22+ class), which 24 satisfies comfortably.
- **Forward note (low):** When this project is revisited after **Oct 2026**, Node 26 becomes the new LTS and is the natural bump. Not a defect today; the spine's "verified current at authoring (2026-06-25)" header already scopes this correctly.
- **Verdict:** Current and correctly characterized. No action for v1.

### 7. `wrangler` (deploy) — VERIFIED ✅
- **Claim:** "current"; deploy via `wrangler pages deploy` (AD-12, Structural Seed).
- **Reality:** Wrangler is on the **v4** major line (v4.0.0 since 2025-03-13; active 4.x development through 2026). It is the current, first-party Cloudflare CLI. Note v4 dropped Node 16 support — irrelevant here since the project targets Node 24.
- **`wrangler pages deploy <dir>` of a pre-built dir — specifically verified:** This command **still works as the spine describes.** Cloudflare's Direct Upload docs (updated April 2026) show exactly `npx wrangler pages deploy ./dist --project-name <name>` to push a folder of prebuilt assets — no host build minutes, creates the project on first run. This is the precise mechanism AD-12 relies on ($0, pre-built `dist/`, no CI). Confirmed live.
- **Verdict:** Current and correctly characterized. No action.

### 8. Cloudflare Pages (host — seed/swappable) — VERIFIED, with a forward flag ⚠️
- **Claim (AD-12 / Stack):** free tier, **unlimited bandwidth**, custom domains, deploy via `wrangler pages deploy`; host is **seed/swappable**.
- **Free tier exists:** ✅ Yes.
- **Unlimited bandwidth:** ✅ Confirmed. Cloudflare's free-plan materials and multiple independent 2026 pricing breakdowns state Pages has **no bandwidth limits on any tier, including free** (unlimited bandwidth + unlimited requests). *Precision note:* the official Pages **Limits** doc no longer enumerates a bandwidth row at all (it lists builds, files, file-size, custom-domain caps), so the "unlimited bandwidth" claim is sourced from the free-plan/pricing pages rather than the Limits table. Still true — just not stated where you'd first look.
- **Custom domains:** ✅ Supported on free. Source numbers vary (official Limits doc says **100 custom domains/project**; one secondary review said 5) — either comfortably exceeds the spine's single `raedmund.com/engineering` need. Auto-SSL included.
- **`wrangler pages deploy`:** ✅ See item 7 — verified live.
- **⚠️ FORWARD FLAG (medium) — Pages is in maintenance mode, Workers is the go-forward host.** This is the one substantive currency finding. Cloudflare is **absorbing Pages into Workers Static Assets**: as of March 2026 Workers has full feature parity with Pages for static assets + custom domains, new platform features ship to **Workers first**, and Cloudflare's own guidance is *"if you're starting a new project, skip Pages entirely — deploy to Workers from day one."* **Pages is NOT deprecated** — there is no forced-migration deadline and it "gets maintenance updates at best" — so **every claim in AD-12 is true today** and Pages will keep serving a static `dist/` for the foreseeable future. But a brand-new greenfield project (June 2026) choosing Pages is choosing the legacy lane of a converging product.
  - **Why this is only MINOR, not STALE:** AD-12 *already* makes the host **explicitly seed/swappable** ("any static host serves `dist/` identically; the recommended default is Cloudflare Pages"). That invariant is exactly the escape hatch — the architecture does not bind to Pages. The deploy command and $0/unlimited-bandwidth properties hold.
  - **Recommendation (non-blocking):** Add a one-line note to AD-12 / the Stack row acknowledging Pages→Workers convergence and naming **Cloudflare Workers Static Assets** (`wrangler deploy` with `assets`/`pages_build_output_dir`) as the equivalent go-forward target. Costs nothing, future-proofs the seed, and is consistent with the spine's own "seed/swappable" framing. No re-architecture required — the swap is a deploy-command change behind the same `dist/` artifact.
- **Verdict:** Claims current and accurate today; flagged for the maintenance-mode trajectory. Swappability invariant already mitigates.

### 9. `launchd` / cron (local scheduler) — VERIFIED ✅
- **Claim:** OS-native weekly scheduler; "never GitHub Actions" (AD-1, FR-7).
- **Reality:** `launchd` (macOS) and `cron` (Unix) are stable OS primitives — no currency concept applies, no deprecation. Correctly characterized as OS-native. On modern macOS `launchd` is indeed the idiomatic choice over the legacy crontab; the spine lists both, which is correct and portable.
- **Verdict:** Current and correctly characterized. No action.

---

## Summary table

| # | Technology | Spine claim | Live reality (mid-2026) | Status |
|---|---|---|---|---|
| 1 | Python | 3.14 | 3.14.0 stable 2025-10-07; on 3.14.6 | ✅ current |
| 2 | `gh` CLI | current | maintained, canonical | ✅ current |
| 3 | `git` | current | universal, stable | ✅ current |
| 4 | `tokei` | current | actively maintained, 14.0.0 (2025-12-30) | ✅ current (note scc alt) |
| 5 | Astro | 6 | 6.0 stable 2026-03-10; latest major | ✅ current |
| 6 | Node.js | 24 LTS | 24 = Active LTS; 26 not LTS until Oct 2026 | ✅ correct LTS |
| 7 | `wrangler` | current | v4 line; `pages deploy <dir>` works (Apr 2026 docs) | ✅ current |
| 8 | Cloudflare Pages | free, unlimited BW, custom domains, swappable | all true today; ⚠️ Pages in maintenance, Workers is go-forward | ⚠️ minor forward flag |
| 9 | `launchd`/cron | OS-native | stable OS primitives | ✅ current |

---

## Findings (ranked)

1. **[medium] Cloudflare Pages is in maintenance mode; Workers Static Assets is the go-forward host.** All AD-12 claims (free, unlimited bandwidth, custom domains, `wrangler pages deploy` of `dist/`) are verified true as of 2026-06-25, but Cloudflare is absorbing Pages into Workers, ships new features to Workers first, and advises new projects to deploy to Workers from day one. Not deprecated, no deadline. **Mitigated** by AD-12's explicit seed/swappable host invariant. *Recommend:* one-line note naming Workers Static Assets as the equivalent forward target.
2. **[low] Node 24 → 26 LTS transition lands Oct 2026.** Node 24 is the correct LTS to target *today*; revisit the version bump after October 2026 when 26 becomes Active LTS. The spine's "verified at authoring (2026-06-25)" framing already scopes this. No action for v1.
3. **[low] `scc` worth recording as the swappable LOC alternative.** tokei is current, maintained, and the right seed default — but mirroring the host's "swappable" treatment, note scc (boyter/scc) as the alternative. Aligns with AD-10's "LOC is supporting cast" and §Deferred's rejection of a complexity model. Cosmetic.
4. **[low] "Unlimited bandwidth" is sourced from pricing/free-plan pages, not the official Pages Limits table.** The Limits doc no longer lists a bandwidth row; the claim remains true (confirmed via free-plan + 2026 pricing sources) but isn't documented where a reader would first check. Worth a source link if the Stack note is ever expanded.

Everything else in the Stack table and ADs is **current and correctly characterized** — Python 3.14, gh, git, tokei, Astro 6, Node 24 LTS, wrangler (incl. the pre-built `pages deploy`), and launchd/cron all check out against live sources with no defects.

---

## Sources
- Python 3.14: https://www.python.org/downloads/release/python-3140/ · https://peps.python.org/pep-0745/ · https://docs.python.org/3/whatsnew/3.14.html
- Astro 6: https://astro.build/blog/astro-6/ · https://docs.astro.build/en/guides/upgrade-to/v6/
- Node.js LTS: https://nodejs.org/en/about/previous-releases · https://endoflife.date/nodejs · https://nodejs.org/en/blog/release/v26.0.0
- tokei: https://github.com/XAMPPRocky/tokei · https://github.com/XAMPPRocky/tokei/releases
- wrangler / Direct Upload: https://developers.cloudflare.com/workers/wrangler/ · https://developers.cloudflare.com/pages/get-started/direct-upload/
- Cloudflare Pages limits & free tier: https://developers.cloudflare.com/pages/platform/limits/ · https://www.cloudflare.com/plans/free/
- Pages → Workers convergence: https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/ · https://developers.cloudflare.com/workers/static-assets/
