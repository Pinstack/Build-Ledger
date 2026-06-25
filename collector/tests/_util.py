"""Shared test helpers: put the collector dir on sys.path and build a known-good document."""
from __future__ import annotations

import sys
from pathlib import Path

COLLECTOR_DIR = Path(__file__).resolve().parent.parent
if str(COLLECTOR_DIR) not in sys.path:
    sys.path.insert(0, str(COLLECTOR_DIR))

import contract  # noqa: E402


def co(total, human, ai_co, agents=(), bots=()):
    block = contract.empty_coauthorship()
    block.update({
        "total_commits": total, "human_commits": human,
        "ai_coauthored_commits": ai_co,
        "ai_coauthored_share": round(ai_co / total, 3) if total else 0.0,
        "agents": [{"author": a, "commits": c} for a, c in agents],
        "excluded_bots": [{"author": a, "commits": c} for a, c in bots],
    })
    return block


def metrics(commits=0, active_days=0, files=0, loc_added=0, loc_removed=0):
    return {"commits": commits, "active_days": active_days, "files": files,
            "loc_added": loc_added, "loc_removed": loc_removed, "loc_net": loc_added - loc_removed}


def signals(t=False, ci=False, mig=False):
    return {"has_tests": t, "has_ci": ci, "has_migrations": mig}


def arts(wi=0, da=0, qc=0):
    return {"workflow_infrastructure": wi, "delivery_artefacts": da, "quality_controls": qc}


def valid_doc():
    """A minimal document that passes BOTH contract.validate() and redaction.assert_safe()."""
    return {
        "schema_version": "1.0.0",
        "ledger_metadata": {
            "generated_at": "2026-06-24T00:00:00Z", "collector_version": "1.0.0",
            "schema_version": "1.0.0", "identities_included": ["Pinstack"],
            "date_range": {"first_commit": "2025-01-01", "latest_commit": "2026-06-24"},
            "data_url": "/build-ledger.json", "methodology_url": "/engineering#methodology",
        },
        "repositories": [
            {"id": "pub1", "display_tier": "public", "allowlisted": False, "status": "active",
             "label": "public-repo", "metrics": metrics(10, 4, 20, 100, 10),
             "signals": signals(True, True, False),
             "coauthorship": co(10, 7, 6, agents=[("cursor[bot]", 2)], bots=[("dependabot", 1)]),
             "ai_artefacts": arts(2, 1, 0)},
            {"id": "priv1", "display_tier": "aggregate_only", "allowlisted": False, "status": "active",
             "metrics": metrics(5, 2, 8, 50, 5), "signals": signals(False, True, False),
             "coauthorship": co(5, 5, 3, agents=[("Cursor Agent", 1)]), "ai_artefacts": arts(1, 0, 0)},
        ],
        "aggregates": {
            "repo_counts": {"public": 1, "private": 1, "archived": 0, "active": 2},
            "languages": [{"name": "Python", "share": 1.0}],
            "totals": {"commits": 15, "user_authored_commits": 12, "loc_net": 135},
            "coauthorship": {"unit": "commit", "total_commits": 15, "human_commits": 12,
                             "agent_authored_commits": 3, "ai_coauthored_commits": 9,
                             "ai_coauthored_share": 0.6,
                             "agents": [{"author": "cursor[bot]", "commits": 2},
                                        {"author": "Cursor Agent", "commits": 1}],
                             "excluded_bots": [{"author": "dependabot", "commits": 1}]},
        },
        "agentic_practice": {"available": True, "cadence": {"sessions_per_week": 12}, "cache_hit_ratio": 0.91,
                             "model_mix": [{"model": "Claude Opus 4.8", "sessions": 10}],
                             "cost": {"available": False, "total": None, "pricing_source": None,
                                      "as_of": None, "trend": [], "confounders": ["project mix"]}},
        "retrospective": {"available": True, "window_view": [{"claim": "Shipped the contract",
                                                              "evidence_ref": "git"}]},
        "in_flight": {"available": True, "wip_branches": 1, "open_issues": 2, "draft_prs": 0,
                      "todo_fixme": 4, "commit_trajectory": [3, 5, 2]},
        "activity": {"available": True,
                     "monthly": [{"month": "2026-01", "commits": 10, "loc_net": 120}],
                     "heatmap": [{"date": "2026-01-05", "commits": 3}]},
        "exclusions": {"forks": 0, "vendored": 1, "generated": 2, "lockfiles": 3,
                       "minified": 0, "bot_commits": 1, "mirrors": 0},
    }
