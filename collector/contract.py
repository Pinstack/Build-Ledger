"""The build-ledger.json contract (FR-8, AD-2, AD-7).

One stable, versioned shape couples the Collector and the Generated Page. This module owns:
  - the schema version + the supported MAJOR,
  - the controlled enums (display_tier, artefact classes, status),
  - typed-empty builders for every Module so a no-data Module is `available: false`
    with the populated shape, never a silent omission or a bare {}/[] (AD-3),
  - a validator that a candidate document either passes or fails with a clear error.

The page reads `ledger_metadata.schema_version` and renders against it; a v1 page refuses an
unsupported MAJOR rather than mis-render (AD-7).
"""
from __future__ import annotations

import re

# --- versions -----------------------------------------------------------------
SCHEMA_VERSION = "1.0.0"     # the contract version (top level == ledger_metadata)
SUPPORTED_MAJOR = 1          # a page/collector built for v1 supports MAJOR 1 only
COLLECTOR_VERSION = "1.0.0"  # the producing collector's own semver

# --- controlled enums ---------------------------------------------------------
DISPLAY_TIERS = ("public", "redacted", "aggregate_only")  # the fixed 3-value enum (AD-4)
ARTEFACT_CLASSES = ("workflow_infrastructure", "delivery_artefacts", "quality_controls")  # FR-4
STATUSES = ("active", "archived")

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


# --- typed-empty Module builders (AD-3) --------------------------------------
def empty_metrics() -> dict:
    return {"commits": 0, "active_days": 0, "files": 0,
            "loc_added": 0, "loc_removed": 0, "loc_net": 0}


def empty_signals() -> dict:
    return {"has_tests": False, "has_ci": False, "has_migrations": False}


def empty_coauthorship() -> dict:
    # Superset of the documented minimal shape: keeps unit/human_commits/agents/excluded_bots
    # (load-bearing) and adds the trailer-based hero figures FR-3 requires (the lower bound).
    return {"unit": "commit", "total_commits": 0, "human_commits": 0,
            "ai_coauthored_commits": 0, "ai_coauthored_share": 0.0,
            "agents": [], "excluded_bots": []}


def empty_artefacts() -> dict:
    return {k: 0 for k in ARTEFACT_CLASSES}


def empty_agentic_practice() -> dict:
    return {"available": False, "cadence": {}, "model_mix": [], "cache_hit_ratio": None,
            "cost": {"available": False, "total": None, "pricing_source": None,
                     "as_of": None, "trend": [], "confounders": []}}


def empty_retrospective() -> dict:
    # Public retrospective carries window_view ONLY — never a mirror_view key (AD-6).
    return {"available": False, "window_view": []}


def empty_in_flight() -> dict:
    return {"available": False, "wip_branches": 0, "open_issues": 0, "draft_prs": 0,
            "todo_fixme": 0, "commit_trajectory": []}


def empty_exclusions() -> dict:
    return {"forks": 0, "vendored": 0, "generated": 0, "lockfiles": 0,
            "minified": 0, "bot_commits": 0, "mirrors": 0}


# --- validation ---------------------------------------------------------------
def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def _validate_repo(r: dict, i: int, errors: list[str]) -> None:
    at = f"repositories[{i}]"
    if not isinstance(r, dict):
        errors.append(f"{at}: not an object")
        return

    _require(isinstance(r.get("id"), str) and bool(r.get("id")), f"{at}.id missing/empty", errors)
    tier = r.get("display_tier")
    _require(tier in DISPLAY_TIERS, f"{at}.display_tier={tier!r} not in {DISPLAY_TIERS}", errors)
    _require(isinstance(r.get("allowlisted"), bool), f"{at}.allowlisted must be bool", errors)
    _require(r.get("status") in STATUSES, f"{at}.status={r.get('status')!r} not in {STATUSES}", errors)

    # label rule keyed to display_tier (AD-4 / Glossary):
    label = r.get("label")
    if tier == "public":
        _require(isinstance(label, str) and bool(label), f"{at}.label required when display_tier=public", errors)
    elif tier == "redacted":
        _require(isinstance(label, str) and bool(label),
                 f"{at}.label (generic) required when display_tier=redacted", errors)
    elif tier == "aggregate_only":
        _require(label in (None, "") or "label" not in r,
                 f"{at}.label must be null/absent when display_tier=aggregate_only (Silhouette)", errors)

    m = r.get("metrics")
    if isinstance(m, dict):
        for k in ("commits", "active_days", "files", "loc_added", "loc_removed", "loc_net"):
            _require(_is_int(m.get(k)), f"{at}.metrics.{k} must be int", errors)
    else:
        errors.append(f"{at}.metrics missing")

    s = r.get("signals")
    if isinstance(s, dict):
        for k in ("has_tests", "has_ci", "has_migrations"):
            _require(isinstance(s.get(k), bool), f"{at}.signals.{k} must be bool", errors)
    else:
        errors.append(f"{at}.signals missing")

    co = r.get("coauthorship")
    if isinstance(co, dict):
        _require(co.get("unit") == "commit", f"{at}.coauthorship.unit must be 'commit' (v1)", errors)
        _require(_is_int(co.get("human_commits")), f"{at}.coauthorship.human_commits must be int", errors)
        for key in ("agents", "excluded_bots"):
            lst = co.get(key)
            if isinstance(lst, list):
                for j, a in enumerate(lst):
                    _require(isinstance(a, dict) and isinstance(a.get("author"), str)
                             and _is_int(a.get("commits")),
                             f"{at}.coauthorship.{key}[{j}] must be {{author:str, commits:int}}", errors)
            else:
                errors.append(f"{at}.coauthorship.{key} must be a list")
    else:
        errors.append(f"{at}.coauthorship missing")

    art = r.get("ai_artefacts")
    if isinstance(art, dict):
        for k in ARTEFACT_CLASSES:
            _require(_is_int(art.get(k)), f"{at}.ai_artefacts.{k} must be int", errors)
    else:
        errors.append(f"{at}.ai_artefacts missing")


def validate(doc: dict) -> list[str]:
    """Return a list of human-readable errors; empty list means the document is contract-valid."""
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["document is not a JSON object"]

    # top-level keys
    for k in ("schema_version", "ledger_metadata", "repositories", "aggregates",
              "agentic_practice", "retrospective", "in_flight", "exclusions"):
        _require(k in doc, f"missing top-level key: {k}", errors)

    sv = doc.get("schema_version")
    _require(isinstance(sv, str) and bool(_SEMVER.match(sv or "")),
             f"schema_version must be semver, got {sv!r}", errors)
    if isinstance(sv, str) and _SEMVER.match(sv):
        major = int(sv.split(".")[0])
        _require(major == SUPPORTED_MAJOR,
                 f"unsupported schema MAJOR {major} (this build supports {SUPPORTED_MAJOR})", errors)

    lm = doc.get("ledger_metadata")
    if isinstance(lm, dict):
        _require(lm.get("schema_version") == sv,
                 "ledger_metadata.schema_version must equal top-level schema_version", errors)
        for k in ("generated_at", "collector_version", "identities_included",
                  "date_range", "data_url", "methodology_url"):
            _require(k in lm, f"ledger_metadata.{k} missing", errors)
        if isinstance(lm.get("date_range"), dict):
            for k in ("first_commit", "latest_commit"):
                _require(k in lm["date_range"], f"ledger_metadata.date_range.{k} missing", errors)
    else:
        errors.append("ledger_metadata missing/invalid")

    repos = doc.get("repositories")
    if isinstance(repos, list):
        for i, r in enumerate(repos):
            _validate_repo(r, i, errors)
    else:
        errors.append("repositories must be a list")

    agg = doc.get("aggregates")
    if isinstance(agg, dict):
        rc = agg.get("repo_counts")
        if isinstance(rc, dict):
            for k in ("public", "private", "archived", "active"):
                _require(_is_int(rc.get(k)), f"aggregates.repo_counts.{k} must be int", errors)
        else:
            errors.append("aggregates.repo_counts missing")
        langs = agg.get("languages")
        _require(isinstance(langs, list), "aggregates.languages must be a list", errors)
        if isinstance(langs, list):
            for j, l in enumerate(langs):
                _require(isinstance(l, dict) and isinstance(l.get("name"), str)
                         and isinstance(l.get("share"), (int, float)) and not isinstance(l.get("share"), bool),
                         f"aggregates.languages[{j}] must be {{name:str, share:number}}", errors)
        tot = agg.get("totals")
        if isinstance(tot, dict):
            for k in ("commits", "user_authored_commits", "loc_net"):
                _require(_is_int(tot.get(k)), f"aggregates.totals.{k} must be int", errors)
        else:
            errors.append("aggregates.totals missing")
    else:
        errors.append("aggregates missing/invalid")

    ap = doc.get("agentic_practice")
    _require(isinstance(ap, dict) and isinstance(ap.get("available"), bool),
             "agentic_practice.available must be bool", errors)

    retro = doc.get("retrospective")
    if isinstance(retro, dict):
        _require(isinstance(retro.get("window_view"), list), "retrospective.window_view must be a list", errors)
        _require("mirror_view" not in retro, "retrospective.mirror_view must NEVER be present (AD-6)", errors)
    else:
        errors.append("retrospective missing/invalid")

    inf = doc.get("in_flight")
    if isinstance(inf, dict):
        for k in ("wip_branches", "open_issues", "draft_prs", "todo_fixme"):
            _require(_is_int(inf.get(k)), f"in_flight.{k} must be int", errors)
        _require(isinstance(inf.get("commit_trajectory"), list), "in_flight.commit_trajectory must be a list", errors)
    else:
        errors.append("in_flight missing/invalid")

    exc = doc.get("exclusions")
    if isinstance(exc, dict):
        for k in ("forks", "vendored", "generated", "lockfiles", "minified", "bot_commits", "mirrors"):
            _require(_is_int(exc.get(k)), f"exclusions.{k} must be int", errors)
    else:
        errors.append("exclusions missing/invalid")

    return errors


def is_valid(doc: dict) -> bool:
    return not validate(doc)
