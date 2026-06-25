#!/usr/bin/env python3
"""Converge the prior published snapshot into the v1 contract (Story 1.6 convergence).

The committed public/build-ledger.json was first produced by the v0.2 spike on the trusted local
machine over the real repositories. This script re-emits that *already-redacted, already-public*
snapshot into the locked v1 contract THROUGH THE SAME assemble()+publish() path the live collector
uses — so the whole-document redaction assert genuinely runs and the result is contract-true. It is
a one-time data convergence for the committed artifact; collect.py (main) remains the ongoing
producer that recomputes everything from source on the local machine.

Honesty notes: the v0.2 snapshot carried commit counts, co-authorship, signals and tracked-file
counts, but NOT per-author agent names, LOC churn, or active-day counts. Those are emitted as
generic buckets / zeros here (never fabricated); the live local run populates them from source.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract  # noqa: E402
from collect import OUT, assemble_document, load_config, publish, tier  # noqa: E402
from modules.artefacts import classify_present  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED_INPUT = HERE / "seed_input.json"


def _artefacts_from_signals(osig: dict, ai_cfg: dict) -> dict:
    present = set(osig.get("ai_artefacts", []) or [])
    if osig.get("has_claude_dir"):
        present.add(".claude")
    return classify_present(present, ai_cfg)


def to_repo_inputs(old: dict, cfg: dict) -> tuple[list[dict], dict]:
    repos_cfg, redaction_cfg, ai_cfg = cfg["repos"], cfg["redaction"], cfg["ai_sources"]
    inputs: list[dict] = []
    for i, r in enumerate(old.get("repositories", [])):
        is_public = r.get("visibility") == "public"
        name = r.get("name")
        # Stable opaque key: real nameWithOwner for public; for an already-redacted private repo we
        # have no name, so derive a stable key from its snapshot position (id stays opaque either way).
        nwo = r.get("repo") or f"private/silhouette-{i:02d}"
        descriptor = {
            "name": name or f"silhouette-{i:02d}",
            "nameWithOwner": nwo,
            "visibility": "PUBLIC" if is_public else "PRIVATE",
            "isArchived": bool(r.get("archived")),
            "isFork": False,
            "isMirror": False,
            "primaryLanguage": ({"name": r["primary_language"]} if r.get("primary_language") else None),
            "createdAt": r.get("created"),
            "pushedAt": r.get("last_active"),
        }
        tiering = tier(descriptor, repos_cfg, redaction_cfg)

        oco = r.get("coauthorship") or {}
        human = int(oco.get("commits_human_authored", 0) or 0)
        agent = int(oco.get("commits_agent_authored", 0) or 0)
        bot = int(oco.get("commits_bot", 0) or 0)
        ai_co = int(oco.get("commits_ai_coauthored", 0) or 0)
        total = int(oco.get("total_commits", human + agent + bot) or 0)
        co = contract.empty_coauthorship()
        co.update({
            "total_commits": total,
            "human_commits": human,
            "ai_coauthored_commits": ai_co,
            "ai_coauthored_share": round(ai_co / total, 3) if total else 0.0,
            "agents": [{"author": "Other agent", "commits": agent}] if agent else [],
            "excluded_bots": [{"author": "Other bot", "commits": bot}] if bot else [],
        })

        osig = r.get("signals") or {}
        sig = {"has_tests": bool(osig.get("has_tests")),
               "has_ci": bool(osig.get("has_ci")),
               "has_migrations": bool(osig.get("has_migrations"))}
        m = contract.empty_metrics()
        m["commits"] = total
        m["files"] = int(osig.get("tracked_files", 0) or 0)
        # active_days + loc churn are not in the v0.2 snapshot -> left 0 (never fabricated)
        arts = _artefacts_from_signals(osig, ai_cfg)

        inputs.append({"descriptor": descriptor, "tiering": tiering, "metrics": m,
                       "signals": sig, "coauthorship": co, "ai_artefacts": arts,
                       "exclusion_tallies": {}})
    return inputs, {"forks": 0, "mirrors": 0}


def main() -> None:
    cfg = load_config()
    old = json.loads(SEED_INPUT.read_text())
    repo_inputs, repo_tallies = to_repo_inputs(old, cfg)

    dates = [d[:10] for ri in repo_inputs for d in
             (ri["descriptor"].get("createdAt"), ri["descriptor"].get("pushedAt")) if d]
    date_range = {"first_commit": min(dates) if dates else None,
                  "latest_commit": max(dates) if dates else None}
    # Preserve the original collection timestamp — the data was collected then, not re-collected now.
    generated_at = (old.get("ledger_metadata", {}) or {}).get("generated") or date_range["latest_commit"]

    doc = assemble_document(repo_inputs, exclusion_repo_tallies=repo_tallies,
                            date_range=date_range, generated_at=generated_at, cfg=cfg)
    publish(doc, OUT, cfg)

    a = doc["aggregates"]
    print(f"OK (converged from snapshot) -> {OUT}")
    print(f"repos: {a['repo_counts']['public']} public + {a['repo_counts']['private']} private "
          f"| commits {a['totals']['commits']} | user-authored {a['totals']['user_authored_commits']}")
    print(f"AI-co-authored share: {a['coauthorship']['ai_coauthored_share']*100:.1f}% "
          f"({a['coauthorship']['ai_coauthored_commits']}/{a['coauthorship']['total_commits']} commits, "
          f"commit-level lower bound) | bot commits excluded: {doc['exclusions']['bot_commits']}")


if __name__ == "__main__":
    main()
