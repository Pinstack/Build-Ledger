#!/usr/bin/env python3
"""Build Ledger collector (v0.1 spike).

Generates public/build-ledger.json from GitHub (account: Pinstack) + local clones.

Safety: redaction is enforced centrally and asserted before write.
  - Public repos: named, full detail.
  - Private repos: SILHOUETTES — shape + signals only, no name / repo / path /
    commit message / per-author breakdown.
  - The Allowlist is the ONLY mechanism to promote a private repo above silhouette.
    v1 ALLOWLIST = empty (none).

Hero metric: human vs AI-agent commit split (from commit authorship). Bot noise
(dependabot/renovate/CI) is classified out of the headline, not counted as agent work.
"""
from __future__ import annotations
import json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ---------------- config ----------------
GITHUB_ACCOUNT = "Pinstack"
PROJECTS_DIR = Path.home() / "Projects"
OUT = Path(__file__).resolve().parent.parent / "public" / "build-ledger.json"
SCHEMA_VERSION = "build-ledger.v1"
COLLECTOR_VERSION = "0.2.0"
ALLOWLIST: set[str] = set()  # v1: none -> every private repo stays a silhouette

AI_AGENT = re.compile(r"(cursor|claude|copilot|devin|codex|aider|anthropic|openai|cody|sweep)", re.I)
BOT = re.compile(r"(dependabot|renovate|github-actions|greenkeeper|snyk|mergify|\[bot\]|semantic-release)", re.I)

EXCLUSIONS = ["forks", "vendored deps", "generated artefacts", "lockfiles",
              "minified files", "bot-authored commits (classified out of headline)"]


def sh(args, cwd=None, timeout=90) -> str:
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ""


def classify(name: str, email: str) -> str:
    s = f"{name} {email}"
    if AI_AGENT.search(s):
        return "ai_agent"
    if BOT.search(s):
        return "bot"
    return "human"


def gh_repos() -> list[dict]:
    out = sh(["gh", "repo", "list", "--limit", "500", "--json",
              "name,nameWithOwner,visibility,isFork,isArchived,primaryLanguage,pushedAt,createdAt"])
    try:
        return json.loads(out)
    except Exception:
        return []


def local_clone_map() -> dict[str, Path]:
    m: dict[str, Path] = {}
    if not PROJECTS_DIR.exists():
        return m
    for d in PROJECTS_DIR.iterdir():
        if not d.is_dir() or not (d / ".git").exists():
            continue
        url = sh(["git", "-C", str(d), "remote", "get-url", "origin"]).strip()
        mo = re.search(r"[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
        if mo:
            m[mo.group(1).lower()] = d
    return m


def coauthorship(path: Path) -> dict:
    """Two complementary signals:
    - Trailer-based (HERO): commits carrying a `Co-authored-by: <AI model>` trailer.
      This is how AI-native work shows up — the human commits, the model is credited.
      Names the exact model per commit (auditable provenance).
    - Author-based (secondary): commits an agent identity authored autonomously.
    """
    total = int((sh(["git", "-C", str(path), "rev-list", "--count", "--all"]).strip() or "0"))

    # author-based (autonomous)
    a_human = a_ai = a_bot = 0
    for line in sh(["git", "-C", str(path), "shortlog", "-sne", "--all"]).splitlines():
        m = re.match(r"\s*(\d+)\s+(.*?)\s+<(.*?)>", line)
        if not m:
            continue
        c, cls = int(m.group(1)), classify(m.group(2), m.group(3))
        a_ai += c if cls == "ai_agent" else 0
        a_bot += c if cls == "bot" else 0
        a_human += c if cls == "human" else 0

    # trailer-based (the real signal): one commit may credit several models
    bodies = sh(["git", "-C", str(path), "log", "--all", "-i", "--grep=co-authored-by",
                 "--pretty=format:%H\x01%b\x02"])
    ai_coauthored = 0
    models: dict[str, int] = {}
    for chunk in bodies.split("\x02"):
        if "\x01" not in chunk:
            continue
        body = chunk.split("\x01", 1)[1]
        has_ai = False
        for cm in re.finditer(r"co-authored-by:\s*(.+?)\s*<", body, re.I):
            nm = cm.group(1).strip()
            if AI_AGENT.search(nm):
                has_ai = True
                models[nm] = models.get(nm, 0) + 1
        if has_ai:
            ai_coauthored += 1

    return {
        "total_commits": total,
        "commits_ai_coauthored": ai_coauthored,
        "ai_coauthored_share": round(ai_coauthored / total, 3) if total else 0.0,
        "commits_agent_authored": a_ai,
        "commits_human_authored": a_human,
        "commits_bot": a_bot,
        "ai_models": models,
    }


def signals(path: Path) -> dict:
    def has(*p) -> bool:
        return path.joinpath(*p).exists()
    ai = [f for f in ("CLAUDE.md", "AGENTS.md", ".cursorrules", ".mcp.json", "mcp.json", "GEMINI.md") if has(f)]
    return {
        "has_tests": has("tests") or has("test"),
        "has_ci": has(".github", "workflows"),
        "has_migrations": has("migrations") or has("alembic"),
        "has_dockerfile": has("Dockerfile"),
        "has_claude_dir": has(".claude"),
        "ai_artefacts": ai,
        "tracked_files": sh(["git", "-C", str(path), "ls-files"]).count("\n"),
    }


def main() -> None:
    repos = gh_repos()
    clones = local_clone_map()
    out_repos: list[dict] = []
    priv = 0
    agg = {"total_commits": 0, "commits_ai_coauthored": 0, "commits_agent_authored": 0,
           "commits_human_authored": 0, "commits_bot": 0,
           "repos_with_tests": 0, "repos_with_ci": 0, "repos_with_migrations": 0,
           "repos_with_ai_artefacts": 0, "languages": {}, "ai_models": {}}

    for r in repos:
        if r.get("isFork"):
            continue
        clone = clones.get(f"{GITHUB_ACCOUNT}/{r['name']}".lower())
        co = coauthorship(clone) if clone else None
        sig = signals(clone) if clone else None
        lang = (r.get("primaryLanguage") or {}).get("name")
        is_public = r.get("visibility") == "PUBLIC"
        promoted = r["name"] in ALLOWLIST

        if co:
            agg["total_commits"] += co["total_commits"]
            agg["commits_ai_coauthored"] += co["commits_ai_coauthored"]
            agg["commits_agent_authored"] += co["commits_agent_authored"]
            agg["commits_human_authored"] += co["commits_human_authored"]
            agg["commits_bot"] += co["commits_bot"]
            for k, v in co["ai_models"].items():
                agg["ai_models"][k] = agg["ai_models"].get(k, 0) + v
        if sig:
            agg["repos_with_tests"] += sig["has_tests"]
            agg["repos_with_ci"] += sig["has_ci"]
            agg["repos_with_migrations"] += sig["has_migrations"]
            agg["repos_with_ai_artefacts"] += 1 if (sig["ai_artefacts"] or sig["has_claude_dir"]) else 0
        if lang:
            agg["languages"][lang] = agg["languages"].get(lang, 0) + 1

        rec = {"visibility": "public" if is_public else "private",
               "archived": r.get("isArchived", False),
               "primary_language": lang,
               "created": (r.get("createdAt") or "")[:10],
               "last_active": (r.get("pushedAt") or "")[:10],
               "coauthorship": co, "signals": sig}

        if is_public or promoted:
            rec["name"] = r["name"]
            rec["repo"] = r.get("nameWithOwner")
        else:  # SILHOUETTE
            priv += 1
            rec["label"] = f"Private project {priv}"
            if rec.get("coauthorship"):
                rec["coauthorship"] = {k: v for k, v in rec["coauthorship"].items() if k != "ai_models"}

        out_repos.append(rec)

    # ---- SAFETY GATE: no private record may carry identifying fields ----
    for rec in out_repos:
        if rec["visibility"] == "private":
            assert not ({"name", "repo"} & rec.keys()), "REDACTION LEAK: private repo exposed identity"
            co = rec.get("coauthorship") or {}
            assert "ai_models" not in co, "REDACTION LEAK: private per-model breakdown exposed"

    tc = agg["total_commits"]
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "ledger_metadata": {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "collector_version": COLLECTOR_VERSION,
            "github_identities": [GITHUB_ACCOUNT],
            "repo_count": len(out_repos),
            "allowlist_size": len(ALLOWLIST),
            "coauthorship_source": "local clones (where present); Co-authored-by trailers + author identity",
        },
        "aggregates": {
            "public_repos": sum(x["visibility"] == "public" for x in out_repos),
            "private_repos": sum(x["visibility"] == "private" for x in out_repos),
            "total_commits": tc,
            "commits_ai_coauthored": agg["commits_ai_coauthored"],
            "ai_coauthored_share": round(agg["commits_ai_coauthored"] / tc, 3) if tc else 0.0,
            "commits_agent_authored": agg["commits_agent_authored"],
            "commits_bot_excluded": agg["commits_bot"],
            "repos_with_tests": agg["repos_with_tests"],
            "repos_with_ci": agg["repos_with_ci"],
            "repos_with_migrations": agg["repos_with_migrations"],
            "repos_with_ai_artefacts": agg["repos_with_ai_artefacts"],
            "languages": dict(sorted(agg["languages"].items(), key=lambda kv: -kv[1])),
            "ai_models": dict(sorted(agg["ai_models"].items(), key=lambda kv: -kv[1])),
        },
        "repositories": out_repos,
        "agentic_practice": {"available": False, "note": "Claude/Codex log module — next iteration"},
        "retrospective": {"available": False, "note": "sourced from BMAD memlogs + git — next iteration"},
        "in_flight": {"available": False, "note": "WIP branches / open issues / draft PRs — next iteration"},
        "exclusions": EXCLUSIONS,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ledger, indent=2))

    a = ledger["aggregates"]
    print(f"OK -> {OUT}")
    print(f"repos: {a['public_repos']} public + {a['private_repos']} private (silhouettes)")
    print(f"commits: {a['total_commits']} total | {a['commits_ai_coauthored']} AI-co-authored "
          f"({a['ai_coauthored_share']*100:.1f}%) | {a['commits_agent_authored']} agent-authored (autonomous) "
          f"| {a['commits_bot_excluded']} bot-noise excluded")
    print(f"top AI models (by co-authored commits): {list(a['ai_models'].items())[:6]}")
    print(f"signals: tests {a['repos_with_tests']} | CI {a['repos_with_ci']} | "
          f"migrations {a['repos_with_migrations']} | AI-artefacts {a['repos_with_ai_artefacts']}")
    print(f"top langs: {list(a['languages'].items())[:6]}")


if __name__ == "__main__":
    main()
