---
review: rubric-walker
gate: Reviewer Gate
target: ARCHITECTURE-SPINE.md (Build Ledger, 2026-06-25)
verdict: SOUND-WITH-NITS
reviewer-altitude: initiative
date: 2026-06-25
---

# Rubric-Walker Review — Architecture Spine: Build Ledger

**Verdict: SOUND-WITH-NITS.** This is a tight, disciplined spine. The privacy boundary — the load-bearing risk for this product — is fixed structurally (tree boundary = privacy boundary), not by discipline, which is the right move and the strongest part of the document. The twelve ADs are mostly genuinely enforceable, the brownfield spike is ratified rather than contradicted, and all thirteen FRs have a home. Findings below are nits and two gaps worth a second look; none are blocking, but the operational-envelope gap (item 7) and the soft-deprecated host default (item 4) deserve a sentence each before this is treated as final.

---

## 1. Does it fix the real divergence points for the level below (seven Modules + the page), missing none?

**PASS.** The level below this spine is: seven Collector Modules built independently + one Astro page. The places they could diverge are all pinned:

- **Modules colliding / cross-writing / vanishing** → AD-3 (one top-level key each, sole writer, `available: false` never silent omission). This is the central anti-divergence rule for the seven-way fan-out and it is precise.
- **Collector and page drifting** → AD-2 (single contract, page renders solely from it) + the dependency-direction diagram (the file is the only membrane).
- **Modules disagreeing on date/share/money/id encoding** → Consistency Conventions table (ISO-8601 UTC, floats 0–1 at 3 dp, money+`pricing_source`+`as_of`, opaque `id`). Good — this is exactly the cross-module formatting divergence that bites when seven units are built in parallel.
- **Page and publish disagreeing on how the file is consumed** → AD-8 (build-time static render, file served beside page).

The seven Modules are each mapped to a file and a key in the Capability→Architecture Map. No divergence point for this level is left unaddressed. Nothing missed.

## 2. Is every AD's Rule ENFORCEABLE and does it actually PREVENT its stated divergence?

**PASS, with two soft spots.** Walking each:

- **AD-1** (local-primary) — enforceable: "runs only on a trusted local machine," "never GitHub Actions," token "local `gh`/env only." Concrete and checkable. Prevents private code reaching third-party CI. **Note:** this AD directly *overrides the PRD*, which repeatedly specifies a "weekly GitHub Action" (FR-7 title, §6.1, §4.7, Platform, Safety "token held by the GitHub Action"). The override is correct on the merits — the PRD's own AD-1-equivalent privacy invariant (private repos never leave the machine) is irreconcilable with cloning ~35 private client repos on a GitHub runner — but see item 5; the spine should say *explicitly* that it supersedes the PRD's GitHub-Action mechanism, because right now a builder reading FR-7 and AD-1 side by side sees a flat contradiction with no note reconciling them.
- **AD-2** (single contract) — enforceable (`schema_version` present; "no other channel couples"). Prevents drift. Good.
- **AD-3** (ownership) — the strongest enforceability in the doc: "owns exactly one top-level key and is the only writer," machine-checkable. 
- **AD-4** (fail-closed whole-doc redaction) — enforceable as an assertion over the whole document, with the fail-closed behavior named ("the run does not publish"). Prevents the leak. Empty Allowlist in v1 makes it maximally safe. Excellent.
- **AD-5** (private outputs outside the tree) — enforceable *by construction* ("the one public repo therefore cannot contain private data structurally"). This is the best kind of rule — it removes the failure mode rather than guarding against it. 
- **AD-6** (mirror never in public file) — machine-checkable ("published `build-ledger.json` has no `retrospective.mirror_view` key"). 
- **AD-7** (semver) — enforceable; the page "declares the MAJOR it supports and refuses an unsupported MAJOR." Concrete.
- **AD-8** (build-time static) — enforceable; "no charting library; islands only where genuinely interactive."
- **AD-9** (aggregate-only, no transcripts) — enforceable as a content assertion ("no raw transcript … ever enters"). Overlaps AD-4's transcript clause but the redundancy is defensible (different framing: AD-4 = the gate, AD-9 = the Module-level rule).
- **AD-10** (anti-vanity) — **softest of the twelve.** "The hero is the Co-Authorship Split … volume is structurally supporting cast" — "structurally supporting cast" is a *presentation* claim, and presentation lives on the page, not in the contract. The genuinely enforceable parts are here ("`unit: commit`" lower-bound marker; "carries no spend/token-leaderboard … structure"), and those *are* checkable against the JSON shape. But "the hero is X" is an aspiration the architecture can't enforce — it's a design/layout decision. This is acceptable at initiative altitude (the contract *enables* the discipline by demoting volume to plain integers and refusing a leaderboard key), but the Rule slightly overreaches by implying it governs page emphasis. Minor.
- **AD-11** (auditable cost or none) — enforceable ("never estimated; an unsourceable figure is omitted"). The pinned-dated-published price table is concrete. Good — and notably this *resolves PRD Open-Q1* (cost-source authority), which is a plus.
- **AD-12** (pre-built local deploy) — enforceable ("deployed pre-built (`dist/`) … no host build minutes"). Prevents CI re-introduction. See item 4 on the named host.

No AD is pure aspiration except the soft edge of AD-10, and even that has an enforceable core. Net: strong.

## 3. Could anything under Deferred let two units diverge?

**PASS.** Six deferred items, each genuinely safe:

- **Line-level Attribution / Acceptance Ratio (FR-13)** — safe because the contract is built *forward-compatibly now*: AD-7 + the `attribution` representation reserve the shape, `coauthorship` carries `unit: "commit"`, and the MINOR-bump rule guarantees a v1 page still renders a v1.5 file. The divergence is pre-empted by today's schema, not deferred into a future collision. This is the model citizen of safe deferral.
- **Representative-systems section** — explicitly "page-content/UX decision, not a structural invariant," addable as an optional key via MINOR. Correctly *not* architecture's call. Safe.
- **git-notes Attribution Store** — a Vision-era evidence *format*, layered after v1.5; touches nothing in v1. Safe.
- **Broader raedmund.com** — out of scope; v1 is the one page. No shared unit. Safe.
- **Build-detail seed owned by the code** (exact `pricing.yml`, tool internals, `config/*.yml` field sets) — correctly deferred to the code: these are within-Module implementation details that don't cross the contract membrane, so they can't make two units diverge. Right call.
- **PRD Vision items + explicitly rejected items** — the rejected-for-v1 list (complexity-scoring model, Cursor/Copilot acceptance APIs) is *stronger* than deferral: it closes the door so a future builder can't reopen a divergence. Good.

Nothing deferred can cause two units to disagree on the contract. The forward-compatible `attribution` reservation is what makes the headline deferral (line-level) genuinely safe rather than a deferred rewrite.

## 4. Is named tech verified-current?

**MOSTLY PASS — one soft-deprecated default to flag.** Verified against live sources (June 2026):

- **Python 3.14** — ✅ current. 3.14.0 shipped Oct 2025; 3.14.6 is the latest patch (June 2026). Correct.
- **Astro 6** — ✅ current stable. Released March 2026; v7 is in beta (7.0.0-beta.3, June 2026) but not stable. Naming "6" is right.
- **Node.js 24 LTS** — ✅ correct and *well-chosen*. 24 is the current Active LTS. Node 26 shipped April 2026 but is **Current, not LTS** until Oct 2026 — so pinning 24 LTS (not 26) is the right production call, not a stale one. Good discipline.
- **tokei** — ✅ actively maintained (XAMPPRocky/tokei), JSON output, gitignore-aware. Appropriate; nothing stale.
- **`wrangler pages deploy`** — ✅ still supported and documented as of April 2026.
- **Cloudflare Pages** — ⚠️ **soft-deprecated.** As of 2026 the Cloudflare Pages docs carry a banner recommending migration to **Workers** (static assets), and Cloudflare is steering new projects to Workers as the unified platform. Compounding this: **Astro 6's headline feature is "first-class Cloudflare Workers support."** So the spine names, as its recommended default, the platform the vendor is actively migrating *away from*, while the chosen framework's marquee integration points at the migration *target*. **This is a low-to-medium nit, not an error**, for two reasons the spine already bakes in: (a) AD-12 explicitly marks the host "seed/swappable … any static host serves `dist/` identically," and (b) `wrangler pages deploy` still works. The fix is one clause: either switch the recommended default to Cloudflare Workers static assets (better aligned with Astro 6 and Cloudflare's direction) or add a one-line note that Pages is in soft-deprecation and Workers is the forward path — so a builder picking the host in three months isn't surprised. The seed/swappable framing means this costs nothing to correct.

No tech "smells stale or unjustified" except the Pages default, which is justified-but-aging.

## 5. Does it RATIFY rather than contradict the brownfield spike?

**PASS.** The spike (`collector/collect.py` v0.2) is named in `sources` and handled explicitly in the Capability→Architecture Map closing note: the convergence deltas (string `schema_version` → semver `1.0.0`; `visibility` → `display_tier` + `allowlisted`; flat artefact list → three Artefact Classes; exclusions list → counts) are called *"a build punch-list, not new decisions."* That is textbook ratification — it adopts the spike's existence and direction, names the precise gaps, and frames closing them as mechanical rather than as a redesign. The spine does not contradict the spike; it absorbs it and tells the builder exactly what to reconcile.

(Caveat noted under item 2/AD-1: the spine *does* contradict the **PRD's** GitHub-Action mechanism — but that's the PRD, not the spike, and it's a correct and necessary override. The spike itself is ratified cleanly.)

## 6. Does it cover the PRD's capabilities (FR-1..FR-13)?

**PASS.** Every FR has an explicit home. Cross-checked the Capability→Architecture Map plus AD `Binds:` lines:

| FR | Home | Verified |
| --- | --- | --- |
| FR-1, FR-2 (repo metrics, volume-as-supporting) | `repos.py` → `repositories[]`/`aggregates` | ✅ AD-2/3/10 |
| FR-3 (co-authorship hero, commit-level) | `coauthorship.py` → `repositories[].coauthorship` | ✅ AD-3/7/10 |
| FR-4 (AI-native artefacts, 3 classes) | `artefacts.py` → `ai_artefacts` | ✅ AD-3 |
| FR-5 (agentic practice) | `practice.py` → `agentic_practice` | ✅ AD-9/11 |
| FR-6 (redaction) | `redaction.py` central gate | ✅ AD-4/5/6 |
| FR-7 (schedule + fast-track) | local `launchd`/cron + manual | ✅ AD-1/12 |
| FR-8 (contract emit) | `collect.py` | ✅ AD-2/3/7 |
| FR-9, FR-10 (page, survive inspection) | `site/` Astro | ✅ AD-2/8/10 |
| FR-11 (retrospective, 2 framings) | `retrospective.py` → `window_view` (+ mirror→drawer) | ✅ AD-6/9 |
| FR-12 (in-flight) | `in_flight.py` → `in_flight` | ✅ AD-3/4 |
| FR-13 (line-level, v1.5) | Deferred via `attribution` MINOR | ✅ AD-7 |

All 13 bound in front-matter `binds:` and traceable. FR-10's "renders without runtime error on Chrome/Safari/Firefox" is implicitly served by AD-8 (static HTML/CSS/SVG, no JS-bundle inspection surface) — a nice structural answer to "survive inspection." Coverage is complete.

## 7. Is every dimension this initiative-altitude spine owns decided, deferred, or an open question — no whole dimension silent, ESPECIALLY the operational/environmental envelope?

**PASS on the envelope, with one genuinely-thin dimension.** This is the item the brief said to check hard, so:

**Operational/environmental envelope — COVERED, and well.** This was a real risk and the spine handles it:
- **Deployment & environments** → AD-8 (build-time static), AD-12 (pre-built `dist/` to free static host, $0), and the Structural Seed diagram which draws the *entire* runtime+deploy+privacy envelope in one view (local machine as sole producer → redaction gate → `dist/` → Cloudflare → route; provenance via git push). This is exactly the operational picture an initiative spine owns.
- **Infra/provider strategy** → AD-1 (local-primary, sole producer), AD-12 (host seed/swappable, named default), Stack table (scheduler = `launchd`/cron OS-native). Provider strategy is explicit.
- **Operations** → Consistency Conventions "State & cross-cutting" row: immutable-per-run, fail-closed errors, stdout audit summary (counts only, never private content), config in `config/*.yml`, auth local-only. Run cadence (weekly local scheduler) and fast-track (manual run) both addressed via AD-1/FR-7.

The operational envelope is **not** silent — it's one of the better-covered dimensions, anchored by a dedicated diagram. Good.

**Thin dimension — observability/failure-recovery for the unattended scheduled run.** The spine nails *publish-time* failure (fail-closed: redaction-assert fails → no publish; Module error → `available: false`). What it does **not** address: when the **local** weekly `launchd`/cron run fails *silently* (machine asleep, `gh` token expired, clone path moved), how does the builder learn the ledger went stale? The PRD names "Freshness & observability" as a cross-cutting NFR (Ledger Metadata makes staleness self-evident *on the page*), and the spine's stdout audit summary covers an *attended* run — but a headless scheduled run on a laptop has no one reading stdout. This isn't a missing *whole dimension* (operations is decided; this is a corner of it), and it may be legitimately below initiative altitude (an epic-level concern), but given the product's entire value is "refreshed weekly" and "staleness is self-evident," a one-line open question — *"how does a failed unattended local run surface?"* — would close it honestly rather than leave it implicit. **Low severity; flag, don't block.**

No other dimension is silent. Security/privacy (over-covered, appropriately), data contract, versioning, render strategy, naming/formats, cost — all decided. State management is explicitly immutable-per-run. Nothing material is missing.

## 8. Are the two mermaid diagrams VALID and do they convey structure?

**PASS.** Parsed both mentally:

- **Diagram 1 (dependency direction, lines 30–34):** `flowchart LR`; three nodes — `mods["…"]`, `contract[("…")]` (cylinder), `page["…"]`; two labelled edges via `-->|"…"|`. Quoted labels correctly absorb the parens/spaces in "Collector Modules (7)" and "Generated Page (Astro)". **Valid.** Conveys real structure: the one-directional pipe and "the file is the membrane" — this diagram *is* the AD it sits under (dependency direction as a rule). Not decorative.
- **Diagram 2 (Structural Seed, lines 126–154):** `flowchart TB`; nested subgraphs (`LOCAL` containing `COLL`) with quoted-bracket labels `subgraph LOCAL["…"]`; node shapes used correctly — cylinders `[("…")]`, hexagon gate `{{"…"}}`, stadium route `(["…"])`, `<br/>` line breaks inside labels; edges plain (`-->`), labelled (`-->|"private framing"|`), and dotted-labelled (`-.->|"git commit + push = provenance trail"|`). Subgraph `end`s balanced (COLL closes, LOCAL closes — two `end` tokens, lines 138–139). **Valid.** Conveys genuine structure: it's the operational envelope from item 7 — privacy boundary as tree boundary, the single redacted crossing, the pre-built deploy path, and the provenance trail. Dense but legible; every node earns its place. Not decorative.

Both parse and both carry load. (Minor stylistic note, non-blocking: Diagram 2 is near the upper bound of how much a single flowchart should carry — if it grows in v1.5 it should split — but at v1 it reads cleanly.)

---

## Summary of findings

| # | Severity | Finding |
| --- | --- | --- |
| 1 | **medium** | **AD-1 silently overrides the PRD's GitHub-Action mechanism.** The override is *correct* (cloning ~35 private repos on a third-party runner violates the privacy invariant), but FR-7/§6.1/Platform/Safety all say "weekly GitHub Action" and AD-1 says "never GitHub Actions" with no reconciling note. Add one sentence to AD-1: "This supersedes the PRD's GitHub-Action scheduling — the privacy invariant forbids a third-party runner; cadence is local." Otherwise a builder hits a flat contradiction. |
| 2 | **low–medium** | **Cloudflare Pages default is soft-deprecated.** Cloudflare's 2026 docs steer new work to Workers; Astro 6's headline integration is Workers, not Pages. `wrangler pages deploy` still works and AD-12 marks the host swappable, so this is a nit — but switch the *recommended default* to Cloudflare Workers static assets, or add a one-line "Pages is in soft-deprecation; Workers is the forward path." Costs nothing given the seed/swappable framing. |
| 3 | **low** | **No surfacing path for a failed unattended local run.** Fail-*closed* at publish is well-handled, but a silently-failed weekly `launchd`/cron run (laptop asleep, token expired) has no reader for its stdout, and "refreshed weekly / staleness self-evident" is core to the product. Add a one-line open question. Possibly epic-altitude, but worth naming. |
| 4 | **low** | **AD-10's "the hero is X / volume is supporting cast" overreaches into page emphasis**, which the contract can't enforce (it's a layout decision). The enforceable core (the `unit: "commit"` lower-bound marker; no leaderboard/spend key in the shape) is present and fine — just tighten the Rule's claim so it governs the *contract* (refuses vanity structure) rather than implying it governs *visual emphasis*. |

**No critical or high findings.** The spine is sound: the privacy boundary is structural, the twelve ADs are mostly hard-enforceable, the spike is ratified, all FRs land, and the operational envelope — the dimension flagged for hard scrutiny — is actually one of the better-covered, anchored by a dedicated and valid diagram. Address #1 and #2 with a sentence each and this is STRONG.
