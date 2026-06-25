"""Activity-over-time (FR-1 supporting; UX-DR1 charts). Owns the top-level `activity` key.

Aggregate across all non-excluded repos: a monthly series (commits + loc_net) and a daily
commit-intensity heatmap. Dates and counts ONLY — never a repo name, path, or message — so it is
Silhouette-safe for private repos (their commit *dates* and *counts* carry no client identity).
`available: false` until a run computes a series from source.
"""
from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path

from contract import empty_activity
from modules.repos import is_excluded_path


def monthly_and_heatmap(dates: list[str]) -> tuple[dict, dict]:
    """Pure: from a list of 'YYYY-MM-DD' commit dates -> ({month: commits}, {date: commits})."""
    monthly: dict[str, int] = defaultdict(int)
    heatmap: dict[str, int] = defaultdict(int)
    for d in dates:
        d = d.strip()
        if len(d) < 10:
            continue
        monthly[d[:7]] += 1
        heatmap[d] += 1
    return dict(monthly), dict(heatmap)


def monthly_loc(numstat_log: str, exclusions_cfg: dict) -> dict:
    """Pure: parse `git log --numstat --date=short --pretty=format:%x01%ad` -> {month: loc_net}.

    Records begin with a \\x01-prefixed date line; subsequent `added\\tremoved\\tpath` lines are
    summed into that month, skipping excluded paths.
    """
    loc: dict[str, int] = defaultdict(int)
    month = None
    for line in numstat_log.splitlines():
        if line.startswith("\x01"):
            month = line[1:].strip()[:7] or None
            continue
        cols = line.split("\t")
        if len(cols) != 3 or month is None:
            continue
        a, d, path = cols
        excl, _ = is_excluded_path(path, exclusions_cfg)
        if excl:
            continue
        loc[month] += (int(a) if a.isdigit() else 0) - (int(d) if d.isdigit() else 0)
    return dict(loc)


def assemble(monthly_commits: dict, monthly_loc_net: dict, heatmap: dict) -> dict:
    act = empty_activity()
    months = sorted(set(monthly_commits) | set(monthly_loc_net))
    act["monthly"] = [{"month": m, "commits": monthly_commits.get(m, 0),
                       "loc_net": monthly_loc_net.get(m, 0)} for m in months]
    act["heatmap"] = [{"date": d, "commits": heatmap[d]} for d in sorted(heatmap)]
    act["available"] = bool(months or heatmap)
    return act


# --- live git path ------------------------------------------------------------
def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args],
                              capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return ""


def compute(clone_paths: list[Path], exclusions_cfg: dict) -> dict:
    """Aggregate activity across the given clones (all repos; output carries no per-repo identity)."""
    all_dates: list[str] = []
    monthly_loc_net: dict[str, int] = defaultdict(int)
    for cp in clone_paths:
        cp = Path(cp)
        all_dates.extend(d for d in _git(["log", "--all", "--pretty=%ad", "--date=short"], cp).splitlines() if d)
        for m, v in monthly_loc(_git(["log", "--all", "--numstat", "--date=short",
                                      "--pretty=format:\x01%ad"], cp), exclusions_cfg).items():
            monthly_loc_net[m] += v
    monthly_commits, heatmap = monthly_and_heatmap(all_dates)
    return assemble(monthly_commits, dict(monthly_loc_net), heatmap)
