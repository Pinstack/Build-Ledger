#!/usr/bin/env python3
"""Build Ledger collector — assembler & entrypoint (FR-7, FR-8; AD-1/2/3/13/14/15).

One run, one file. The pipeline order is pinned (AD-15):
    discover -> TIERING (assign display_tier + stable id) -> per-repo Module contributions
    -> AGGREGATION (derived projection, AD-14) -> whole-document REDACTION assert (AD-4)
    -> atomic write.

The assembler is the sole owner of repositories[] and the stable `id`s; per-repo Modules return
their own field-path only and are merged by id (AD-13). A degraded Module yields typed-empty data
and the run continues; a redaction-assert failure aborts the publish entirely (fail-closed).

This is the trusted-local-machine entrypoint (AD-1): it needs `gh` for discovery and local clones
under ~/Projects for the commit-level signals. Where those are absent it still emits a schema-valid,
redaction-safe (empty) document rather than failing — and the committed public artifact is produced
through the very same assemble()+publish() path by seed.py from the builder's prior real data.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # make contract/modules importable

import yaml  # noqa: E402

import contract  # noqa: E402
import redaction  # noqa: E402
from modules import artefacts, coauthorship, repos  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(__file__).resolve().parent / "config"
OUT = ROOT / "public" / "build-ledger.json"
PRIVATE_DRAWER = Path(os.environ.get("BUILD_LEDGER_PRIVATE", "~/.build-ledger/private")).expanduser()
PROJECTS_DIR = Path(os.environ.get("BUILD_LEDGER_PROJECTS", "~/Projects")).expanduser()


# --- config -------------------------------------------------------------------
def load_config(config_dir: Path = CONFIG_DIR) -> dict:
    cfg = {}
    for name in ("identity", "repos", "redaction", "exclusions", "ai_sources", "pricing"):
        path = config_dir / f"{name}.yml"
        cfg[name] = yaml.safe_load(path.read_text()) if path.exists() else {}
    return cfg


# --- tiering (first pipeline stage, AD-15) -----------------------------------
def stable_id(name_with_owner: str) -> str:
    """A stable, opaque id. A one-way hash so a private repo's id reveals nothing (AD-4/AD-13)."""
    return hashlib.sha256(name_with_owner.encode("utf-8")).hexdigest()[:12]


def tier(descriptor: dict, repos_cfg: dict, redaction_cfg: dict) -> dict:
    """Assign display_tier + label + allowlisted to one repo. Private defaults to a Silhouette;
    the Allowlist is the only promotion path (empty in v1 -> every private repo aggregate_only)."""
    name = descriptor.get("name") or (descriptor.get("nameWithOwner") or "").split("/")[-1]
    is_public = (descriptor.get("visibility") or "").upper() == "PUBLIC"
    allowlist = set(repos_cfg.get("allowlist", []) or [])
    overrides = repos_cfg.get("overrides", {}) or {}
    default_private = (redaction_cfg or {}).get("default_private_tier", "aggregate_only")

    if is_public:
        ov = overrides.get(name, {})
        return {"display_tier": "public", "allowlisted": False,
                "label": ov.get("label", name), "category": ov.get("category")}

    # private repo
    if name in allowlist:
        ov = overrides.get(name, {})
        dt = ov.get("display_tier", "redacted")
        if dt == "public":
            return {"display_tier": "public", "allowlisted": True,
                    "label": ov.get("label", name), "category": ov.get("category")}
        if dt == "redacted":
            generic = (redaction_cfg.get("controlled_vocabulary", {}) or {}).get(
                "generic_repo_category", "Private software system")
            return {"display_tier": "redacted", "allowlisted": True,
                    "label": ov.get("label", generic), "category": generic}
    return {"display_tier": default_private, "allowlisted": False, "label": None, "category": None}


# --- row construction ---------------------------------------------------------
def build_row(descriptor: dict, tiering: dict, metrics: dict, signals: dict,
              coauth: dict, arts: dict) -> dict:
    """Assemble one repositories[] row. Private rows carry NO name/path (Silhouette by construction)."""
    row = {
        "id": stable_id(descriptor.get("nameWithOwner") or descriptor.get("name") or ""),
        "display_tier": tiering["display_tier"],
        "allowlisted": tiering["allowlisted"],
        "status": "archived" if descriptor.get("isArchived") else "active",
        "metrics": metrics,
        "signals": signals,
        "coauthorship": coauth,
        "ai_artefacts": arts,
    }
    if tiering["display_tier"] == "public":
        row["label"] = tiering["label"]
        if tiering.get("category"):
            row["category"] = tiering["category"]
    elif tiering["display_tier"] == "redacted":
        row["label"] = tiering["label"]
        row["category"] = tiering.get("category")
    # aggregate_only -> no label key at all (Silhouette)
    return row


# --- aggregation (derived projection, AD-14) ---------------------------------
def _lang_name(raw, allowed: set[str]) -> str:
    if isinstance(raw, dict):
        raw = raw.get("name")
    return raw if raw in allowed else "Other"


def aggregate(rows: list[dict], descriptors: list[dict], redaction_cfg: dict) -> dict:
    total = len(rows)
    public = sum(1 for r in rows if r["display_tier"] == "public")
    archived = sum(1 for r in rows if r["status"] == "archived")
    allowed_langs = set((redaction_cfg.get("controlled_vocabulary", {}) or {}).get("languages", [])) | {"Other"}

    lang_counts: dict[str, int] = {}
    for d in descriptors:
        name = _lang_name(d.get("primaryLanguage") or d.get("primary_language"), allowed_langs)
        if name and not (isinstance(name, str) and name.lower() == "none"):
            lang_counts[name] = lang_counts.get(name, 0) + 1
    languages = [{"name": n, "share": round(c / total, 3) if total else 0.0}
                 for n, c in sorted(lang_counts.items(), key=lambda kv: (-kv[1], kv[0]))]

    commits = sum(r["metrics"]["commits"] for r in rows)
    human = sum(r["coauthorship"]["human_commits"] for r in rows)
    ai_co = sum(r["coauthorship"]["ai_coauthored_commits"] for r in rows)
    agent_authored = sum(sum(a["commits"] for a in r["coauthorship"]["agents"]) for r in rows)
    co_total = sum(r["coauthorship"]["total_commits"] for r in rows)
    loc_net = sum(r["metrics"]["loc_net"] for r in rows)

    agent_tot: dict[str, int] = {}
    bot_tot: dict[str, int] = {}
    for r in rows:
        for a in r["coauthorship"]["agents"]:
            agent_tot[a["author"]] = agent_tot.get(a["author"], 0) + a["commits"]
        for b in r["coauthorship"]["excluded_bots"]:
            bot_tot[b["author"]] = bot_tot.get(b["author"], 0) + b["commits"]

    return {
        "repo_counts": {"public": public, "private": total - public,
                        "archived": archived, "active": total - archived},
        "languages": languages,
        "totals": {"commits": commits, "user_authored_commits": human, "loc_net": loc_net},
        # additive derived projection for the hero (AD-14); pure function of the rows above.
        "coauthorship": {
            "unit": "commit", "total_commits": co_total, "human_commits": human,
            "agent_authored_commits": agent_authored,
            "ai_coauthored_commits": ai_co,
            "ai_coauthored_share": round(ai_co / co_total, 3) if co_total else 0.0,
            "agents": [{"author": a, "commits": c} for a, c in sorted(agent_tot.items(), key=lambda kv: -kv[1])],
            "excluded_bots": [{"author": b, "commits": c} for b, c in sorted(bot_tot.items(), key=lambda kv: -kv[1])],
        },
    }


# --- assembly -----------------------------------------------------------------
def assemble_document(repo_inputs: list[dict], *, exclusion_repo_tallies: dict,
                      date_range: dict, generated_at: str, cfg: dict) -> dict:
    """Build the whole document in memory from already-tiered per-repo inputs (single source of
    truth for both the live run and the data-convergence seed)."""
    redaction_cfg = cfg.get("redaction", {})
    rows: list[dict] = []
    excl = contract.empty_exclusions()
    excl["forks"] = exclusion_repo_tallies.get("forks", 0)
    excl["mirrors"] = exclusion_repo_tallies.get("mirrors", 0)

    for ri in repo_inputs:
        row = build_row(ri["descriptor"], ri["tiering"], ri["metrics"], ri["signals"],
                        ri["coauthorship"], ri["ai_artefacts"])
        rows.append(row)
        for k in ("vendored", "generated", "lockfiles", "minified"):
            excl[k] += ri.get("exclusion_tallies", {}).get(k, 0)
        excl["bot_commits"] += sum(b["commits"] for b in ri["coauthorship"]["excluded_bots"])

    # deterministic order (AD-15): by status then id (no dates that could churn ordering)
    rows.sort(key=lambda r: (r["status"], r["id"]))
    descriptors = [ri["descriptor"] for ri in repo_inputs]
    aggregates = aggregate(rows, descriptors, redaction_cfg)

    identity = cfg.get("identity", {})
    doc = {
        "schema_version": contract.SCHEMA_VERSION,
        "ledger_metadata": {
            "generated_at": generated_at,
            "collector_version": contract.COLLECTOR_VERSION,
            "schema_version": contract.SCHEMA_VERSION,
            "identities_included": (identity.get("subject", {}) or {}).get("github_identities", []),
            "date_range": date_range,
            "data_url": identity.get("data_url", "/build-ledger.json"),
            "methodology_url": identity.get("methodology_url", "/engineering#methodology"),
        },
        "repositories": rows,
        "aggregates": aggregates,
        "agentic_practice": contract.empty_agentic_practice(),
        "retrospective": contract.empty_retrospective(),
        "in_flight": contract.empty_in_flight(),
        "exclusions": excl,
    }
    return doc


# --- publish (validate -> redact -> atomic write; fail-closed) ----------------
def publish(doc: dict, out_path: Path, cfg: dict, *, write_mirror: dict | None = None) -> None:
    errors = contract.validate(doc)
    if errors:
        raise SystemExit("ABORT: document is not schema-valid:\n  - " + "\n  - ".join(errors))

    # whole-document redaction assert — fail-closed (AD-4). Mutates nothing.
    redaction.assert_safe(doc, redaction_cfg=cfg.get("redaction", {}), ai_cfg=cfg.get("ai_sources", {}))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), prefix=".bl-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp, out_path)  # atomic
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

    # The Mirror is written ONLY to the out-of-tree private drawer, never the public file (AD-5/AD-6).
    if write_mirror is not None:
        PRIVATE_DRAWER.mkdir(parents=True, exist_ok=True)
        (PRIVATE_DRAWER / "mirror.json").write_text(
            json.dumps(write_mirror, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- live run (trusted local machine) -----------------------------------------
def collect_live(cfg: dict) -> list[dict]:
    exclusions_cfg = cfg.get("exclusions", {})
    ai_cfg = cfg.get("ai_sources", {})
    repos_cfg = cfg.get("repos", {})
    redaction_cfg = cfg.get("redaction", {})

    descriptors = repos.discover(cfg.get("identity", {}))
    repo_inputs: list[dict] = []
    forks = mirrors = 0
    for d in descriptors:
        if d.get("isFork"):
            forks += 1
            continue
        if d.get("isMirror"):
            mirrors += 1
            continue
        clone = PROJECTS_DIR / (d.get("name") or "")
        tiering = tier(d, repos_cfg, redaction_cfg)
        if clone.exists() and (clone / ".git").exists():
            m, sig, tallies = repos.metrics(clone, exclusions_cfg)
            co = coauthorship.compute(clone, ai_cfg)
            arts = artefacts.detect(clone, ai_cfg)
        else:  # degraded: no clone -> typed-empty (run continues, AD-3)
            m, sig, tallies = contract.empty_metrics(), contract.empty_signals(), {}
            co, arts = contract.empty_coauthorship(), contract.empty_artefacts()
        repo_inputs.append({"descriptor": d, "tiering": tiering, "metrics": m, "signals": sig,
                            "coauthorship": co, "ai_artefacts": arts, "exclusion_tallies": tallies})
    return repo_inputs, {"forks": forks, "mirrors": mirrors}


def main() -> None:
    cfg = load_config()
    repo_inputs, repo_tallies = collect_live(cfg)
    dates = []
    for ri in repo_inputs:
        for key in ("createdAt", "pushedAt"):
            v = ri["descriptor"].get(key)
            if v:
                dates.append(v[:10])
    date_range = {"first_commit": min(dates) if dates else None,
                  "latest_commit": max(dates) if dates else None}
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = assemble_document(repo_inputs, exclusion_repo_tallies=repo_tallies,
                            date_range=date_range, generated_at=generated_at, cfg=cfg)
    publish(doc, OUT, cfg)
    a = doc["aggregates"]
    print(f"OK -> {OUT}")
    print(f"repos: {a['repo_counts']['public']} public + {a['repo_counts']['private']} private "
          f"| commits {a['totals']['commits']} | AI-co-authored share "
          f"{a['coauthorship']['ai_coauthored_share']*100:.1f}% (commit-level lower bound)")


if __name__ == "__main__":
    main()
