"""Co-Authorship Split — the hero (FR-3, AD-10). Owns repositories[].coauthorship.

Commit-level only in v1. Two complementary, source-derived facets:
  - the trailer-based AI-co-authored share (the headline) — commits carrying a
    `Co-authored-by: <agent>` trailer over the non-bot total. Stated as an explicit LOWER BOUND:
    trailers are the weakest of four Attribution Layers and miss hand-committed AI code.
  - the author-based breakdown — human author, named agent authors (cursor[bot], Cursor Agent),
    and excluded bot authors (dependabot) distinguished from genuine agents.

Author/bot display names are mapped to a controlled vocabulary; an unrecognised author is bucketed
to a generic token, so no human or client name can ever surface here (feeds the AD-4 guarantee).
The forward-compatible line-level `attribution` representation (FR-13) is reserved for v1.5 and is
NOT emitted in v1 (the v1 `coauthorship.unit == "commit"` is left untouched, AD-7).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from contract import empty_coauthorship


def _patterns(vocab: list[str]) -> list[re.Pattern]:
    return [re.compile(re.escape(v), re.I) for v in vocab]


def _canonical(name: str, vocab: list[str], generic: str) -> str:
    """Return the controlled-vocabulary name that matches `name`, else the generic bucket token."""
    for v in vocab:
        if re.search(re.escape(v), name, re.I):
            return v
    return generic


def classify_author(name: str, email: str, ai_cfg: dict) -> str:
    """agent | bot | human — agents win over bots so `cursor[bot]` is an agent, not bot noise."""
    blob = f"{name} {email}"
    for p in _patterns(ai_cfg.get("agents", [])):
        if p.search(blob):
            return "agent"
    for p in _patterns(ai_cfg.get("bots", [])):
        if p.search(blob):
            return "bot"
    # a bare "[bot]" suffix with no known identity is still bot noise, not a genuine agent
    if "[bot]" in blob.lower():
        return "bot"
    return "human"


def parse_authors(shortlog_text: str, ai_cfg: dict) -> dict:
    """Pure parse of `git shortlog -sne --all` output into the author-based breakdown."""
    agents_vocab = ai_cfg.get("agents", [])
    bots_vocab = ai_cfg.get("bots", [])
    human_commits = bot_commits = 0
    agents: dict[str, int] = {}
    bots: dict[str, int] = {}
    line_re = re.compile(r"^\s*(\d+)\s+(.*?)\s+<(.*?)>\s*$")
    for line in shortlog_text.splitlines():
        m = line_re.match(line)
        if not m:
            continue
        count, name, email = int(m.group(1)), m.group(2), m.group(3)
        cls = classify_author(name, email, ai_cfg)
        if cls == "agent":
            key = _canonical(f"{name} {email}", agents_vocab, "Other agent")
            agents[key] = agents.get(key, 0) + count
        elif cls == "bot":
            key = _canonical(f"{name} {email}", bots_vocab, "Other bot")
            bots[key] = bots.get(key, 0) + count
            bot_commits += count
        else:
            human_commits += count
    return {
        "human_commits": human_commits,
        "agent_authored_commits": sum(agents.values()),
        "bot_commits": bot_commits,
        "agents": [{"author": a, "commits": c} for a, c in sorted(agents.items(), key=lambda kv: -kv[1])],
        "excluded_bots": [{"author": b, "commits": c} for b, c in sorted(bots.items(), key=lambda kv: -kv[1])],
    }


def count_ai_coauthored(log_bodies: str, ai_cfg: dict) -> int:
    """Pure count of commits whose body carries a `Co-authored-by:` trailer naming a known agent.

    `log_bodies` is `git log --all --pretty=format:%H<US>%b<RS>` text (records split on \\x02).
    """
    agent_pats = _patterns(ai_cfg.get("agents", []))
    n = 0
    for chunk in log_bodies.split("\x02"):
        if "\x01" not in chunk:
            continue
        body = chunk.split("\x01", 1)[1]
        for cm in re.finditer(r"co-authored-by:\s*(.+?)\s*<", body, re.I):
            who = cm.group(1)
            if any(p.search(who) for p in agent_pats):
                n += 1
                break
    return n


def assemble(authors: dict, ai_coauthored: int) -> dict:
    """Combine the author breakdown + trailer count into the contract coauthorship block.

    `total_commits` is ALL commits (human + agent + bot) so the AI-co-authored share has the plain,
    reconcilable denominator a skeptic checks ("N of M commits carry an AI co-author trailer").
    Bots are excluded from the *agent* count (excluded_bots), not from the commit total.
    """
    total = authors["human_commits"] + authors["agent_authored_commits"] + authors["bot_commits"]
    block = empty_coauthorship()
    block.update({
        "total_commits": total,
        "human_commits": authors["human_commits"],
        "ai_coauthored_commits": ai_coauthored,
        "ai_coauthored_share": round(ai_coauthored / total, 3) if total else 0.0,
        "agents": authors["agents"],
        "excluded_bots": authors["excluded_bots"],
    })
    return block


# --- live git path (runs on the trusted local machine; graceful elsewhere) ----
def _git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args],
                              capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def compute(clone_path: Path, ai_cfg: dict) -> dict:
    """Compute the coauthorship block for one repo from its local clone."""
    clone_path = Path(clone_path)
    shortlog = _git(["shortlog", "-sne", "--all"], clone_path)
    bodies = _git(["log", "--all", "-i", "--grep=co-authored-by", "--pretty=format:%H\x01%b\x02"], clone_path)
    authors = parse_authors(shortlog, ai_cfg)
    ai_coauthored = count_ai_coauthored(bodies, ai_cfg)
    return assemble(authors, ai_coauthored)
