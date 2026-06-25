---
title: "Build Ledger"
status: final
created: 2026-06-24
updated: 2026-06-24
---

# Product Brief: Build Ledger

**An auditable proof-of-work ledger for AI-native engineering — a window for others, a mirror for you.**

## Executive Summary

Build Ledger is a public, inspectable record of *how* Raedmund builds software with AI agents — generated from his real repositories, not hand-authored, and refreshed weekly. It turns the usually-invisible evidence of agentic work — agent instruction files, MCP tooling, orchestration code, evals, and the shipped systems themselves — into something a skeptic can open and verify. It is an **evidence ledger, not a productivity score**: it states what the evidence demonstrates rather than leaving the reader to infer it.

It serves two readers, and the central insight is that they're the same artifact. **Outwardly**, it's the receipts behind an application to GL's *FDE — Agentic Solutions* role, whose bar is "show me the most complex thing you've shipped, and how you'd build it with agents today," and which screens hard for people who can tell elegant agentic work from fragile or fake. **Inwardly**, it's a personal instrument — a mirror that tells Raedmund whether he's growing, where his leverage is, and how his craft is changing. A ledger genuinely useful to *him* reads as *more* authentic to GL, because self-directed honesty can't be faked: build for the mirror, and the window comes free.

The proof is already in the ground. Raedmund is a **fully AI-native engineer** (no traditional hand-coding background), and his git history is itself auditable evidence: the flagship system *Meshic* (5,511 files, 1,434 commits) carries named co-authors — Raedmund alongside `cursor[bot]` and `Cursor Agent` — beside `CLAUDE.md`, `AGENTS.md`, CI, and tests. Real systems, built agentically, provable from source — exactly what GL is hiring for, with receipts.

## The Problem

Two people feel this pain.

**The builder.** AI-native engineers produce real, substantial work — but the proof is invisible or easily dismissed. GitHub's graph rewards streaks, not judgment. "AI wrote it" flattens months of architecture and orchestration into a punchline. There's no honest way to show *how* you work with agents — only *that* you committed code. With no traditional-seniority fallback, the work has to speak entirely for itself.

**The evaluator.** People hiring for agentic engineering can't separate genuine practitioners from vibe-coders. The signal they want — can this person drive agents to ship complex systems *and* critically judge the output? — isn't on a CV or a contribution graph. The GL post is this pain said aloud: it demands shipped complexity *and* method, and pre-screens out anyone uneasy with "AI writes most of the code."

Both fallbacks fail: a CV over-claims and can't be inspected; a raw GitHub profile under-explains and buries the AI-native signal. Neither answers the only question that matters — *"is this real, and how do I know?"*

## The Solution

A page at `raedmund.com/engineering`, generated from Raedmund's GitHub and refreshed weekly, that presents his engineering as auditable evidence — organised around *how the work was built* rather than how much exists. Because every figure is computed from source, derived and re-derived from the repositories themselves, none can be hand-flattered.

Its spine is **AI-native artefacts as evidence**, drawn from sources nobody else triangulates:
- **Git co-authorship** — agents named in commit metadata (the un-fakeable hero signal).
- **Agentic artefacts** — `CLAUDE.md`/`AGENTS.md`, MCP tooling, orchestration code, eval harnesses: a *system around the models*, not chatting with them.
- **Agentic practice** — cadence, method, and efficiency drawn (privacy-safely) from local Claude Code and Codex logs.

Around that spine sit the conventional facts (repos, languages, tests, CI, migrations) — to substantiate, not headline — plus a short *"what this proves"* layer, and two loop-closing sections: an honest **retrospective** (judgment on display) and an auditable **"in-flight"** view (what's moving now, from live repo signals). The page is an executive index; deeper evidence drills down behind it.

A deliberate second-order effect: an automated, auditable pipeline that discovers repos, computes the evidence, reflects on itself, and republishes weekly *is* the loop GL is hiring for — ambiguity → working agentic proof → executive-readable, LLMOps-grade output. The artifact demonstrates the very skill it documents.

## What Makes This Different

- **Triangulated agentic evidence — genuine whitespace.** No tool (GitHub stats, readme-stats, WakaTime, CodersRank, git-of-theseus) surfaces AI instruction files, co-authorship, or orchestration as proof-of-work — let alone corroborates them across three independent auditable sources (git + Claude logs + Codex logs). They treat these as config; Build Ledger treats them as *the* signal.
- **Anti-vanity as positioning.** The only players on the AI axis — Viberank, CCgather — rank by token spend. Build Ledger refuses that. Where it touches spend at all, it's **efficiency-as-craft** (cache-hit discipline, cost-aware model routing, your own trend over time), framed as judgment, never consumption.
- **Auditable by construction.** Generated from source, with a transparent methodology and a prominent "excluded from counts" note (forks, vendored, generated, bots) that pre-empts the "inflated LOC" objection. Every receipt is one click from its claim.
- **The honest risk, named.** If the AI-provenance layer is thin, this collapses into "a nicer GitHub profile." Provenance stays the headline; volume stays supporting cast. The v1 scope enforces it.

## Who This Serves

**The mirror — Raedmund himself.** A personal instrument that answers "am I growing or just busy?", "which systems are alive?", "is my craft deepening?" — and compounds with every build. This is the foundation, not an afterthought: it's *why* the artifact is honest.

**The window — the GL hiring manager (and evaluators like them).** Agentic-native, product- and systems-minded, time-poor, hype-allergic. They *inspect*, not skim, and they grade taste ("elegant, fragile, or fundamentally flawed"). Success is them opening the receipts, finding them real and well-judged, and wanting a conversation. The "evaluators like them" framing keeps the asset alive beyond this one application.

**Future readers** — clients, collaborators, other agentic roles — who ask the same "is this real?" question.

## Success Criteria

**Primary (near-term, binary):** the cold GL DM earns a **substantive human reply** — a real response, not silence. Everything downstream follows from clearing it.

**Quality signals:**
- A skeptical, agentic-native reader inspects it and finds it credible — methodology holds, nothing over-claims.
- The AI-provenance evidence is legible in under a minute.
- It survives a "fragile or flawed?" read — the page itself is elegant and doesn't break. (It is a work sample.)
- *(Mirror)* Raedmund returns to it unprompted, because it tells him something true about his own work.

**Anti-signal (failure):** the takeaway is "nice stats page," not "this person genuinely builds with agents — and I can prove it."

## Scope

The surface has grown from "a page" to a small **multi-source system** — which is why the collector gets a lean PRD before it's built: the `build-ledger.json` schema and redaction over real private *client* repos are invariants you don't want to discover by churning through them.

**In — v1 (narrow but real, generated, inspectable):**
- An **automated collector** computing every figure from source (nothing hand-typed), emitting `build-ledger.json` → a generated page + weekly refresh.
- **Modules:** repo / language / maturity signals · git **co-authorship** (hero) · AI-native artefacts · **agentic practice & efficiency** (Claude/Codex logs, privacy-safe: cache-hit, model mix, honest cost, cadence) · **retrospective** (sourced from BMAD memlogs + git) · auditable **"in-flight"** (live repo signals).
- **Safe-by-default redaction:** private repos become silhouettes (shape + signals, no names/paths/messages).
- Lead with **proof of judgement** (tests/CI/migrations, co-authorship, AI evidence); raw LOC demoted to supporting.
- A visible methodology + "excluded from counts" note.

**Fast-track to the DM:** the weekly schedule is the last switch, not the blocker — one manual generated cut can back the DM, then automation follows.

**Out — v1 (deferred to Vision):** full per-figure badge UI; the six-pack evidence ecosystem; a complexity-scoring model; momentum/decay windows; the private redacted verification bundle; export packs; leaderboard breadth.

The discipline: **narrow and bulletproof** — few modules, generated from source, done flawlessly. A flaky auto-pipeline is a worse work sample than a clean small one.

## Guardrails & Anti-Goals

Worthless the moment it over-claims — and worse than worthless to *this* reader. Non-negotiable:
- No invented token usage, no productivity multipliers, no unverifiable metrics; **not a productivity score** (and the page says so).
- Spend appears only as **efficiency-as-craft**, never a consumption brag; confounders named honestly.
- The **retrospective** reads as confident growth, not self-flagellation — brutally honest in the private mirror, curated in the public window.
- The **"in-flight"** view is auditable (live signals), never an aspirational roadmap.
- Superlatives stay measured ("largest *measured* codebase"); no bare "most complex".
- No exposure of private repo data, client names, or raw transcripts / commit messages — aggregate signals only.
- Every claim is inspectable, or it doesn't ship.

## Vision

With the live page in place, Build Ledger closes the loop — **agents → ledger → retrospective → next build** — becoming an *operating system for Raedmund's own engineering*, not just a page. From there: the full repository portfolio with multi-tier redaction; the six-pack evidence ecosystem; a transparent complexity-scoring model; momentum trends; and a private redacted **verification bundle** for selected reviewers. Further out it generalises beyond Raedmund — an auditable, anti-vanity standard for evidencing *how* engineers work with agents, in a market that increasingly needs one. The GL application is simply its first real user.
