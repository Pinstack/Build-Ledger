# Validation Report — Build Ledger

- **PRD:** `/Users/raedmund/Projects/Build-Ledger/_bmad-output/planning-artifacts/prds/prd-Build-Ledger-2026-06-24/prd.md`
- **Rubric:** `/Users/raedmund/Projects/Build-Ledger/.claude/skills/bmad-prd/assets/prd-validation-checklist.md`
- **Run at:** 2026-06-24T21:42:00Z
- **Grade:** Excellent
- **Mode:** Re-validation (critique only — PRD unmodified)

## Overall verdict

This is now a strong, thesis-driven capability spec whose two stated reasons-to-exist — the `build-ledger.json` contract and the Redaction Rules — are genuinely *locked* rather than aspirational. The re-validation confirms **all six prior findings are resolved**: the CRITICAL `mirror_view` leak path is closed at four independent points (schema, FR-6, FR-11, and a dedicated API-Contracts paragraph) with a test fixture that asserts the key's absence; the redaction contract is now whole-document and fail-closed; the `visibility` enum has been replaced by an orthogonal `display_tier` + `allowlisted` model that restores the addendum's three tiers and separates sensitivity from mechanism; and the two open items that sat on the invariants (Allowlist seed, Mirror View exposure) have been decided and moved to a "Resolved" subsection.

The v1.5 additions (FR-13 line-level, SM-6 acceptance ratio, the forward-compatible `attribution` block) are cleanly fenced out of v1 scope and do not leak into §6.1; v1 stays lean. The cut apparatus (trust-modes, per-figure badges) is not reintroduced — and the `confidence: "inferred"` *field* inside the v1.5 `attribution` schema is a per-method data attribute, not the cut "Inferred" badge UI. **Gate verdict: safe to green-light to architecture/build.** Residual issues are medium-or-lower and none block: a small cluster of judgment-predicate consequences a story author must operationalize, three still-open questions (none on a safety invariant), and a minor Assumptions-Index roundtrip nit.

## Delta vs prior review (1 CRITICAL + 5 HIGH — all resolved)

- ✅ **CRITICAL** — public schema could hold `retrospective.mirror_view` → **RESOLVED**. Removed from the public schema; routed to a separate `private/mirror.json`; absence is a machine-checkable consequence in FR-6 + FR-11 + the test fixture.
- ✅ **HIGH** — redaction contract scoped to repository objects only → **RESOLVED**. Replaced by a whole-document "Global redaction invariant" naming all five public blocks, asserted before publish, fail-closed.
- ✅ **HIGH** — `visibility` enum collapsed the three privacy tiers and conflated tier with mechanism → **RESOLVED**. `display_tier` (3 values: `public`/`redacted`/`aggregate_only`) is the sensitivity axis; `allowlisted` (boolean) is the orthogonal mechanism axis; the `redacted` tier and a `category` field are now representable.
- ✅ **HIGH** — Q4 (Mirror View exposure) was a privacy decision masquerading as an open question → **RESOLVED**. Decided ("no — private-only") and moved to §8 *Resolved*.
- ✅ **HIGH** — two open items (Q1 Allowlist seed, Q4) sat on the locked invariants → **RESOLVED**. Both relocated to §8 *Resolved*; the Allowlist-empty default is stated as a decision and enforced by FR-6.
- ✅ **HIGH (cluster, 5th)** — overlapping redaction-scope / visibility-enum / open-items-on-invariants, plus lossy SM cross-refs → **RESOLVED**. SM-1 now enumerates FR-1…FR-12 explicitly and SM-2 now validates FR-8.

## Dimension verdicts

- Decision-readiness — strong
- Substance over theater — strong
- Strategic coherence — strong
- Done-ness clarity — adequate
- Scope honesty — strong
- Downstream usability — strong
- Shape fit — strong

## Findings by severity

### Critical (0)

None. The prior CRITICAL (`mirror_view` leak path) is resolved.

### High (0)

None. All five prior HIGH findings are resolved.

### Medium (1)

**[Done-ness clarity]** — A handful of consequences rest on judgment predicates (§4.1 FR-2 "bare superlative"; §4.5 FR-11 "self-flagellation")
Not machine-decidable; a story author will operationalize them as copy-review gates. Each is paired with a testable clause, so no FR is left without a verifiable consequence.
Fix: Optionally convert to an enumerated check (forbidden-superlative list for FR-2; "every Window-View line resolves to a source" already covers FR-11's real intent).

### Low (1)

**[Strategic coherence]** — SM↔FR coverage is near-complete; FR-7 leans on composite SMs only (§7)
FR-7 (schedule/fast-track) is validated by SM-4 and listed in SM-1's end-to-end set, so it is covered — but only via composite SMs, never on its own. Acceptable for a single-operator pipeline.
Fix: None required; noted for traceability only.

## Mechanical notes

- **Glossary drift — none material.** "Artefact" (British -e-) held consistently across §3, §4.3, FR-4, and the schema key `ai_artefacts`. The six new terms are spelled/cased consistently with their schema/FR uses (`display_tier`, `allowlisted`, `attribution`, `acceptance_ratio`). No "artifact"/synonym intrusions in the FR/Glossary surface.
- **ID continuity.** FR-1…FR-13 present and unique (FR-13 added; non-contiguous by section, self-acknowledged, all cross-refs resolve). UJ-1…UJ-4 contiguous, each with a named protagonist. SM-1…SM-6 + SM-C1…SM-C3 unique (SM-6 added, tagged v1.5). Prior SM-1 range-notation fragility fixed (now an explicit FR list).
- **Assumptions Index roundtrip — one nit remains.** §9 now indexes the FR-5 logs, §8 Q3 hosting, Performance, **and** §Platform mobile assumptions (the prior two missing entries added). Remaining nit: §9 also carries promoted/settled entries (former Q1 Allowlist; upstream-settled inputs) that are narrative rather than inline `[ASSUMPTION]` tags — acceptable as traceability, but not strict roundtrip pairs. No orphan index entries.
- **§8 numbering.** Open Questions renumber to 1–3 after two were relocated to *Resolved*; §9 references "former §8 Q1" and "§8 Q3," and the Resolved entries cite their enforcement locations. Cross-refs resolve; the renumber is internally consistent.
- **`schema_version` duplication is intentional.** Top-level and inside `ledger_metadata`; §Versioning states the latter is what the page displays. Documented redundancy — leave as-is.
- **Caveat — could not open `reference-dashboard-mockup.pdf`.** The PRD's *description* of the mockup was evaluated for internal consistency (holds across brief/addendum/PRD), but the source artifact itself was not inspected.

## Reviewer files

- `review-rubric.md`
