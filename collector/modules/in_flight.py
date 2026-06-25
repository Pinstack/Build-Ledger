"""In-Flight — auditable live signals only (FR-12). Owns the top-level `in_flight` key.

WIP branches, open issues, draft PRs, in-code work-markers (TODO/FIXME), and commit trajectory —
each backed by a signal present at run time, never an aspirational roadmap. Aggregate counts only;
no branch names, issue titles, or paths surface (Silhouette-safe for private repos).
"""
from __future__ import annotations

import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from contract import empty_in_flight

_MAIN_BRANCHES = {"main", "master", "HEAD", "develop", "trunk"}


def count_wip_branches(branch_lines: list[str]) -> int:
    """Pure: from `git branch -a --format=%(refname:short)` lines, count non-mainline branches."""
    n = 0
    for b in branch_lines:
        name = b.strip().split("/")[-1]
        if not name or "->" in b:
            continue
        if name in _MAIN_BRANCHES:
            continue
        n += 1
    return n


def trajectory_from_dates(dates: list[str], weeks: int = 12, today: str | None = None) -> list[int]:
    """Pure: commits per ISO week for the trailing `weeks` weeks (oldest→newest), aggregate counts."""
    end = date.fromisoformat(today) if today else None
    if end is None and dates:
        end = max(date.fromisoformat(d) for d in dates if len(d) >= 10)
    if end is None:
        return [0] * weeks
    start = end - timedelta(weeks=weeks)
    buckets = [0] * weeks
    for d in dates:
        if len(d) < 10:
            continue
        dd = date.fromisoformat(d[:10])
        if dd <= start or dd > end:
            continue
        idx = min(weeks - 1, (dd - start).days // 7)
        buckets[idx] += 1
    return buckets


def count_todo_fixme(grep_output: str) -> int:
    """Pure: count TODO/FIXME marker lines (counts only — the matched text is never emitted)."""
    return sum(1 for line in grep_output.splitlines() if line.strip())


# --- live path ----------------------------------------------------------------
def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args],
                              capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def _grep_todos(cwd: Path) -> str:
    try:
        # -I skip binary, -r recurse; we keep only the COUNT, never the matched lines/paths
        return subprocess.run(["grep", "-rInE", r"\b(TODO|FIXME|HACK|XXX)\b", str(cwd)],
                              capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def compute(clone_paths: list[Path]) -> dict:
    inf = empty_in_flight()
    if not clone_paths:
        return inf
    all_dates: list[str] = []
    wip = todos = 0
    for cp in clone_paths:
        cp = Path(cp)
        wip += count_wip_branches(_git(["branch", "-a", "--format=%(refname:short)"], cp).splitlines())
        todos += count_todo_fixme(_grep_todos(cp))
        all_dates.extend(d for d in _git(["log", "--all", "--pretty=%ad", "--date=short"], cp).splitlines() if d)
    inf.update({
        "available": True,
        "wip_branches": wip,
        "open_issues": 0,   # populated via `gh` per-repo aggregate where available
        "draft_prs": 0,
        "todo_fixme": todos,
        "commit_trajectory": trajectory_from_dates(all_dates),
    })
    return inf
