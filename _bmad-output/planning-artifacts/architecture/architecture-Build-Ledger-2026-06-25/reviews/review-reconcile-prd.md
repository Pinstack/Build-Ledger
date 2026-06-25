---
title: 'Reconciliation Review — PRD vs Architecture Spine'
type: review
review-kind: reconcile-prd
subject: Build Ledger v1
spine: 'architecture-Build-Ledger-2026-06-25/ARCHITECTURE-SPINE.md'
prd: 'prd-Build-Ledger-2026-06-24/prd.md'
reviewer: reconciliation-reviewer
created: '2026-06-25'
verdict: MINOR GAPS
---

# Reconciliation Review — PRD requires, did the Spine honor it?

**Scope of this review.** I read the driving PRD and the distilled architecture spine and report *only* what the PRD requires that the spine **failed to honor or quietly dropped** — with weight on quiet requirements (a tone, a safety constraint, a testable consequence, a forward-compat rule) that a terse AD structure can flatten away. I do **not** flag the spine for failing to restate build details that the code legitimately owns or that are correctly parked under Deferred. A finding qualifies only when it is a PRD invariant/constraint/FR that **two independently-built units could diverge on**, which the spine neither (a) fixes as an AD, (b) captures as a convention, (c) maps in the Capability→Architecture table, nor (d) names under Deferred.

**Verdict: MINOR GAPS.** The spine is unusually faithful. Every FR (FR-1…FR-13) has an explicit home; the six load-bearing contracts I was asked to stress (global redaction, module-availability, forward-compatible attribution, mirror-never-publishes, provenance-first/anti-vanity, semantic versioning) are each captured as a named `[ADOPTED]` AD with a machine-checkable consequence. The gaps that remain are narrow but real: one **safety mechanism** the PRD specifies positively that the spine encodes only negatively (controlled vocabulary for free-text blocks), one **PRD-vs-spine contradiction** that the spine resolved correctly but silently (weekly cadence: GitHub Action vs local scheduler), and one **forward-compat nuance** (the `redacted` tier must stay representable) that rides only on incorporation-by-reference rather than being nailed the way attribution forward-compat is.

---

## What the spine honored well (so it is not re-litigated below)

- **FR coverage is complete.** FR-1…FR-12 each appear in the Capability→Architecture map with a governing AD; FR-13 + the Acceptance Ratio are correctly under **Deferred** (v1.5, MINOR bump). No homeless FR.
- **Global redaction (FR-6) — negative half, fully.** AD-4 fixes safe-by-default `aggregate_only`, the empty Allowlist, and a **whole-document, fail-closed** assert that enumerates every public block (`repositories[]`, `aggregates`, `agentic_practice` incl. free-text confounders, `retrospective.window_view`, `in_flight`). The prohibited-field list is faithful (name/path/branch/commit message/client name/secret/transcript). AD-5 adds the structural backstop (private outputs live outside the repo tree). This is honored.
- **Mirror-never-publishes (FR-6/FR-11).** AD-6 carries the exact machine-checkable consequence: the published `build-ledger.json` has no `retrospective.mirror_view` key; the mirror goes to the private drawer (AD-5) and is never linked. Honored.
- **Forward-compatible attribution (FR-13/FR-8).** AD-7 + Deferred reproduce the worked example precisely — optional multi-layer `attribution` lands as a MINOR `→1.1.0` bump, v1 `coauthorship` (`unit: "commit"`) untouched, v1 page ignores `attribution`, v1.5 page falls back to commit-level when absent. Honored.
- **Provenance-first / anti-vanity (FR-2/FR-3).** AD-10 captures the structural stance: hero = Co-Authorship Split + AI-Native Artefacts; volume is supporting cast; commit share rendered as an explicit lower bound (`unit: "commit"`); **no** spend/token leaderboard, "Wrapped" recap, or live-counter structure, in any version; Acceptance Ratio is the only sanctioned quality signal and itself not a maximization target. AD-9 (no raw transcripts) and AD-11 (auditable cost or none) round out the anti-vanity posture. Honored.
- **Module-availability (FR-8).** AD-3 is actually **stronger** than the PRD shape: the PRD shows an `available` flag only on `agentic_practice`, whereas AD-3 mandates `available: false` + empty sub-objects for *any* module with no data this run, "never silent omission." Honored (and improved).
- **Semantic versioning (FR-8) and build-time static render (FR-9/FR-10).** AD-7 and AD-8 reproduce the semver rules (MINOR additive non-breaking; MAJOR breaking + page refuses unsupported MAJOR) and the static-render posture (server-generated inline SVG, JSON served beside the page to diff). Honored.

---

## Findings (gaps only)

### F1 — [medium] Free-text blocks: the PRD mandates a *controlled vocabulary* (a positive allowlist); the spine encodes only the *negative* assert (a denylist)

**PRD requires.** The Global redaction contract (§ API Contracts) is explicit that the hardest redaction case — human-authored free text — is handled by *construction*, not just by scanning:

> "Free-text-bearing blocks (`agentic_practice` confounders, `in_flight`, aggregate language/model labels) carry only aggregate integers/labels **drawn from a controlled vocabulary**."

This is a distinct, stronger guarantee than the whole-document assert. The assert is a **denylist** ("no prohibited string appears anywhere"); the controlled-vocabulary rule is an **allowlist** ("these blocks may only contain values from a fixed enum"). The PRD pairs them deliberately because a denylist over free text a human typed is the weakest link in the redaction story — a novel client name or path the scanner's patterns don't anticipate sails through a denylist but is structurally impossible under an allowlist.

**Spine status.** AD-4 lists `agentic_practice` confounders and the free-text blocks as things the **assert** covers ("incl. free-text confounders"), and the Consistency Conventions row says free-text-bearing blocks "carry only aggregate integers/labels" — but **the controlled-vocabulary / enum constraint is dropped.** The convention table actually softens it to "labels," with no statement that those labels are drawn from a fixed, reviewable vocabulary rather than free-typed. Nowhere is the positive mechanism fixed as an AD, captured as a convention, or deferred.

**Why two units diverge.** The Retrospective module author and the Agentic-Practice module author each emit `confounders` / labels. One reads AD-4 as "the central gate scans my output, so I can write a natural-language confounder note" (denylist-trusting). The other reads the PRD and emits only enum tokens from a `config`-defined vocabulary (allowlist). Both pass the assert on benign data; only the second is safe against an unanticipated identifying string in a confounder note — which is exactly the `cost.confounders` case the PRD calls out by name as "especially" sensitive. This is a genuine safety gap, not a restatement nit.

**Suggested resolution.** Add to AD-4 (or as a Convention row): free-text-bearing public blocks (`agentic_practice.cost.confounders`, `in_flight`, aggregate language/model labels) emit **only** values drawn from a controlled vocabulary defined in reviewable `config/*.yml`; the whole-document assert is the backstop, not the primary mechanism, for these blocks.

---

### F2 — [high] Weekly cadence: the PRD says **GitHub Action**, the spine says **local scheduler, never GitHub Actions** — a real contradiction the spine resolved correctly but **silently**

**PRD requires.** The PRD names a GitHub Action as the weekly trigger, repeatedly and as a load-bearing detail, not a passing example:
- FR-7 title: "Run on schedule and on demand (fast-track)" — body: "triggered **weekly by a GitHub Action** and manually on demand."
- §4.7: "the Collector runs (on a **weekly GitHub Action** **and** on manual trigger)."
- §6.1: "**Weekly refresh (GitHub Action)** and manual trigger."
- Platform §: "**weekly via a scheduled GitHub Action**, plus manual trigger."
- Safety §: "Authentication to Pinstack uses a secret token **held by the GitHub Action**."
- Cross-Cutting NFR (Performance): "the weekly run completes within a normal **GitHub Action budget**."

**Spine status.** AD-1 (Local-primary runtime) directly **overrides** this: "Weekly cadence is a **local scheduler** (`launchd`/cron), **never GitHub Actions**." AD-12 reinforces "no GitHub Actions." This is the *correct* resolution — it is forced by the PRD's own Privacy section and AD-1's rationale (private client code and the auth token must never transit a third-party runner; ~35 private client repos are cloned locally). The local-primary reading is the safe one and arguably the only one consistent with FR-6.

**The gap is the silence.** The spine flips an explicitly-stated PRD mechanism without ever flagging that it is contradicting the PRD, and without reconciling the PRD's now-dangling claims:
- The Safety bullet "secret token **held by the GitHub Action**" is left homeless. The spine does cover the new reality elsewhere ("Auth: local `gh`/env token only"), so the token *home* is fine — but a builder cross-reading the PRD Safety section against the spine sees an unreconciled conflict about *where the token lives and what holds it*.
- The Cross-Cutting NFR "within a normal GitHub Action budget" no longer has a referent; the performance envelope for a `launchd`/cron run is unstated (likely fine — local runs are unbudgeted — but the NFR is silently voided rather than restated).

**Why two units diverge.** A builder implementing FR-7 straight from the PRD scaffolds a `.github/workflows/*.yml` with a `schedule:` cron and a repo secret for the token. A builder reading the spine wires `launchd`/cron locally and a local `gh` token. These are incompatible runtime topologies for the single most security-sensitive seam in the system. The spine should explicitly **name the override** so no unit builds the Action path.

**Suggested resolution.** Add a one-line reconciliation note to AD-1 (or the Capability map FR-7 row): "Supersedes the PRD's 'weekly GitHub Action' (FR-7, §4.7, §6.1, Platform, Safety, Performance-NFR): the weekly trigger is a **local** `launchd`/cron job; no GitHub Action runs the Collector. The PRD's 'token held by the Action' and 'GitHub Action budget' are reconciled to local `gh`/env auth and an unbudgeted local run." This converts a silent contradiction into an auditable decision.

---

### F3 — [low] The `redacted` display tier must stay **representable** (three-valued enum) even though v1 never uses it — forward-compat rides only on incorporation-by-reference

**PRD requires.** `display_tier` ∈ {`public`, `redacted`, `aggregate_only`} is a three-value enum. The Glossary is explicit that v1 exercises only two of them *but the third must remain defined and representable*:

> "v1 uses only `public` … and `aggregate_only` …, because the Allowlist is empty; **`redacted` is defined and representable but unused** until a repository is explicitly promoted."

This is a deliberate forward-compat rule: the moment the Allowlist gains an entry (post-v1), a promoted repo may land at `redacted` (generic description, no name), and the contract + page must already accommodate it without a schema break.

**Spine status.** AD-4 says every private repo defaults to `aggregate_only` and the Allowlist ships empty — true for v1, but stated in a way that could read as "only two tiers exist." The `label`/`category` convention row implicitly acknowledges the middle tier ("generic `category` for non-public") but never states that the enum stays **three-valued** or that the promotion path to `redacted` must remain representable. AD-2 makes the PRD shape authoritative by reference, and the PRD shape does list three values — so this is *covered by reference*, not dropped outright. But contrast AD-7, where the spine nails forward-compat for attribution explicitly and with a worked example; the tier forward-compat gets no equivalent guard.

**Why a unit might diverge.** Reading "Allowlist empty → every private repo is a Silhouette" without the Glossary, a module author could model `display_tier` as a two-value boolean-ish enum (`public | aggregate_only`) — simpler, and lossless for v1 data. That choice silently breaks the first post-v1 promotion to `redacted` (a MAJOR-flavored break the AD-7 machinery is supposed to prevent). Low severity because (a) it bites only post-v1 and (b) AD-2's incorporation-by-reference technically already binds the three-value shape — but it is the kind of quiet forward-compat rule the terse structure flattened, and one explicit clause would close it.

**Suggested resolution.** One clause on AD-4 or the conventions row: "`display_tier` stays a three-value enum (`public`/`redacted`/`aggregate_only`); `redacted` is unused in v1 (empty Allowlist) but must remain representable so a later promotion needs no schema break (parallels AD-7 forward-compat)."

---

## Considered and deliberately NOT flagged (with reasoning)

These looked like candidate gaps on a first pass; on inspection each is either covered, correctly the code's to own, or correctly deferred. Recorded so the absence is auditable.

- **"One interaction from evidence" / Methodology Note + Excluded-from-counts Note rendered on the page (FR-3, FR-9, FR-1).** These are Page-content/UX consequences over a contract the spine adopts by reference (AD-2 makes the PRD `build-ledger.json` shape — which carries `exclusions`, `methodology_url`, `data_url`, and the per-author `coauthorship` summary — authoritative). AD-8 adds "JSON served beside the page so a reader can diff." The data needed to back "one click from evidence" is in the referenced contract; *how* the page links it is code/design the spine correctly does not restate. **Not a structural divergence.**
- **Reproducibility / determinism-of-exclusions NFRs.** AD-2 ("removing the Collector does not change what a given file can display") + AD-8 (build-time static render) + the immutable-per-run convention encode "a given file fully determines the page." Determinism of exclusions is a code property over `config/exclusions.yml`. **Covered / code-owned.**
- **Browser support — "renders without runtime error on Chrome/Safari/Firefox" (FR-10, Platform).** A page build-quality detail; AD-8 (static HTML/CSS/SVG, islands only where genuinely interactive) structurally supports a no-runtime-error surface. **Code-owned build detail.**
- **Cost-source authority (PRD Open-Q1).** Genuinely open in the PRD, but AD-11 actually *resolves* the architecture-relevant slice (pinned/dated/published in-repo price table + source link, source + as-of shown on page) and adds `as_of` to the Money convention. **Over-delivered, not a gap.**
- **Archived-repos-included-but-labelled (FR-1); secrets never on the public surface (Safety).** `status: active|archived` is in the referenced shape; "secret" is in AD-4's prohibited-field list. **Covered / code-owned.**
- **Exact copy/tone rules** — the framing sentence "This is not a productivity score…", "no bare superlative," "boring-on-purpose" voice (Aesthetic & Tone, FR-2). The *structural* anti-vanity half is in AD-10; the literal copy is page-content below an architecture spine's altitude. **Correctly out of scope.**
- **Representative-systems section, broader raedmund.com, git-notes store, momentum/decay, export packs, standing OTel collector, complexity-scoring model, Cursor/Copilot APIs.** All explicitly under **Deferred** (and the rejected-for-v1 items called out as rejected, not merely deferred). **Correctly parked.**

---

## Bottom line

The spine did its job as a build substrate: every FR is placed, and all six load-bearing contracts survive distillation with machine-checkable consequences intact — in two cases (module-availability, cost) the spine is stronger than the PRD. The residue is three narrow items: **F1** (controlled-vocabulary mechanism for free-text blocks — the one finding that is a genuine *safety* under-specification, medium), **F2** (the GitHub-Action→local-scheduler override is correct but unflagged, leaving the PRD's Action-bound token/budget claims unreconciled — high because it concerns the most security-sensitive seam and produces incompatible runtime topologies), and **F3** (keep the `redacted` tier representable — low, forward-compat). None require re-architecting; each closes with one explicit clause.
