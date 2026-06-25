"""Repository discovery + base metrics + maturity signals (FR-1). Owns repositories[].metrics
and .signals, and supplies the per-repo exclusion tallies the assembler sums into `exclusions`.

Conventional facts computed from source, with the Excluded-from-counts list applied BEFORE any
figure (forks/mirrors at the repo level; vendored/generated/lockfiles/minified at the path level;
bot-authored commits via the coauthorship Module). Volume substantiates; it never headlines (FR-2).
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path

from contract import empty_metrics, empty_signals


# --- discovery ----------------------------------------------------------------
def discover(identity_cfg: dict) -> list[dict]:
    """Discover repos accessible to the configured identity via local `gh`. Empty if gh absent
    (the live scan is a trusted-local-machine capability, AD-1)."""
    accounts = (identity_cfg.get("subject", {}) or {}).get("github_identities", []) or []
    out: list[dict] = []
    for acct in accounts:
        try:
            res = subprocess.run(
                ["gh", "repo", "list", acct, "--limit", "1000", "--json",
                 "name,nameWithOwner,visibility,isFork,isArchived,isMirror,primaryLanguage,pushedAt,createdAt"],
                capture_output=True, text=True, timeout=120)
            out.extend(json.loads(res.stdout or "[]"))
        except Exception:
            continue
    return out


# --- exclusion classification (pure) -----------------------------------------
def is_excluded_path(path: str, exclusions_cfg: dict) -> tuple[bool, str | None]:
    """Classify a repo-relative path against the exclusion config.

    Returns (excluded, bucket) where bucket is one of the contract exclusion keys
    (vendored/generated/lockfiles/minified) or None when not excluded. Binary/data files are
    excluded from counts but carry no contract bucket -> ("", None)-style handled by caller.
    """
    paths = exclusions_cfg.get("paths", {}) or {}
    parts = path.replace("\\", "/").split("/")
    base = parts[-1]

    vendored_dirs = {"node_modules", "vendor", "third_party", ".venv", "venv", "env"}
    for d in paths.get("dirs", []) or []:
        if d in parts:
            return True, ("vendored" if d in vendored_dirs else "generated")
    if base in set(paths.get("lockfiles", []) or []):
        return True, "lockfiles"
    for g in paths.get("generated_globs", []) or []:
        if fnmatch.fnmatch(base, g):
            return True, ("minified" if ".min." in base else "generated")
    if any(fnmatch.fnmatch(base, g) for g in (paths.get("binary_or_data_globs", []) or [])):
        return True, None  # excluded from counts, no contract bucket
    return False, None


# --- signals (pure) -----------------------------------------------------------
def detect_signals(paths: list[str]) -> dict:
    """Detect maturity signals from a repo-relative path listing (pure / testable)."""
    sig = empty_signals()
    for raw in paths:
        p = raw.replace("\\", "/")
        low = p.lower()
        segs = low.split("/")
        base = segs[-1]
        if (("tests" in segs or "test" in segs or "__tests__" in segs)
                or base.startswith("test_") or base.endswith("_test.py")
                or ".test." in base or ".spec." in base or base.endswith("_test.go")):
            sig["has_tests"] = True
        if (low.startswith(".github/workflows/") or "/.github/workflows/" in low
                or base in (".gitlab-ci.yml", ".travis.yml") or ".circleci" in segs
                or "azure-pipelines.yml" in base):
            sig["has_ci"] = True
        if ("migrations" in segs or "alembic" in segs
                or (segs[:2] == ["prisma", "migrations"]) or "/migrations/" in low):
            sig["has_migrations"] = True
    return sig


# --- live git path ------------------------------------------------------------
def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args],
                              capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return ""


def list_files(clone_path: Path) -> list[str]:
    text = _git(["ls-files"], Path(clone_path))
    return [l for l in text.splitlines() if l]


def metrics(clone_path: Path, exclusions_cfg: dict) -> tuple[dict, dict, dict]:
    """Compute (metrics_block, signals_block, exclusion_tallies) for one repo from its clone."""
    clone_path = Path(clone_path)
    files = list_files(clone_path)

    tallies = {"vendored": 0, "generated": 0, "lockfiles": 0, "minified": 0}
    counted_files: list[str] = []
    for f in files:
        excluded, bucket = is_excluded_path(f, exclusions_cfg)
        if excluded:
            if bucket in tallies:
                tallies[bucket] += 1
            continue
        counted_files.append(f)

    m = empty_metrics()
    commits = _git(["rev-list", "--count", "--all"], clone_path).strip()
    m["commits"] = int(commits) if commits.isdigit() else 0
    dates = {d for d in _git(["log", "--all", "--pretty=%ad", "--date=short"], clone_path).splitlines() if d}
    m["active_days"] = len(dates)
    m["files"] = len(counted_files)

    added = removed = 0
    excluded_names = set()  # cache decisions for numstat paths
    for line in _git(["log", "--all", "--numstat", "--pretty=tformat:"], clone_path).splitlines():
        cols = line.split("\t")
        if len(cols) != 3:
            continue
        a, d, path = cols
        if path not in excluded_names:
            excl, _ = is_excluded_path(path, exclusions_cfg)
            if excl:
                excluded_names.add(path)
                continue
        else:
            continue
        added += int(a) if a.isdigit() else 0
        removed += int(d) if d.isdigit() else 0
    m["loc_added"], m["loc_removed"], m["loc_net"] = added, removed, added - removed

    sig = detect_signals(files)
    return m, sig, tallies
