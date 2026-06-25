"""Agentic Practice & Efficiency (FR-5, AD-9, AD-11). Owns the top-level `agentic_practice` key.

Aggregate-only signals from local Claude Code + Codex logs: cadence, model mix, cache-hit ratio,
and honest cost. NEVER reads or emits transcript / session-log TEXT — only counts, model names, and
token totals (AD-9). Cost is auditable-or-none (AD-11): computed only from a pinned, dated price
table (config/pricing.yml); if that is unset, cost is OMITTED, never estimated. Framed as
efficiency-as-craft, never a leaderboard (AD-10). Degrades to available:false if logs are absent.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from contract import empty_agentic_practice

# Confounders are drawn from the controlled vocabulary (redaction.yml) so the free-text-bearing
# cost.confounders field can never carry a novel client name (AD-4).
_DEFAULT_CONFOUNDERS = ["project mix", "model-price changes"]


def _norm_model(raw: str) -> str:
    """Normalise a raw model id to a stable display label (controlled, vendor-prefixed)."""
    if not raw:
        return "unknown"
    return str(raw)


def aggregate_sessions(sessions: list[dict], pricing: dict | None = None,
                       confounders: list[str] | None = None) -> dict:
    """Pure: a list of per-session SUMMARY dicts -> the agentic_practice block.

    Each session summary: {model, week, input_tokens, output_tokens, cache_read_tokens,
    cache_creation_tokens}. No transcript text is present in or required by this function.
    """
    ap = empty_agentic_practice()
    if not sessions:
        return ap  # available stays False

    weeks = {s.get("week") for s in sessions if s.get("week")}
    n = len(sessions)
    model_counts = Counter(_norm_model(s.get("model", "unknown")) for s in sessions)
    total_in = sum(int(s.get("input_tokens", 0) or 0) for s in sessions)
    total_cache_read = sum(int(s.get("cache_read_tokens", 0) or 0) for s in sessions)
    total_cache_create = sum(int(s.get("cache_creation_tokens", 0) or 0) for s in sessions)
    total_out = sum(int(s.get("output_tokens", 0) or 0) for s in sessions)

    denom = total_in + total_cache_read + total_cache_create
    cache_hit_ratio = round(total_cache_read / denom, 3) if denom else None

    ap.update({
        "available": True,
        "cadence": {"sessions": n, "weeks_active": len(weeks),
                    "sessions_per_week": round(n / len(weeks), 2) if weeks else None},
        "model_mix": [{"model": m, "sessions": c, "share": round(c / n, 3)}
                      for m, c in model_counts.most_common()],
        "cache_hit_ratio": cache_hit_ratio,
        "cost": _cost(sessions, pricing, confounders or _DEFAULT_CONFOUNDERS),
    })
    return ap


def _cost(sessions: list[dict], pricing: dict | None, confounders: list[str]) -> dict:
    """Auditable-or-none (AD-11). Cost only if pricing.yml is pinned (as_of + source_url + prices);
    otherwise omitted (available:false, total:null) — never estimated."""
    base = {"available": False, "total": None, "pricing_source": None, "as_of": None,
            "trend": [], "confounders": confounders}
    pricing = pricing or {}
    prices = pricing.get("prices") or {}
    if not (pricing.get("as_of") and pricing.get("source_url") and prices):
        return base  # unsourceable -> omit, do not guess

    total = 0.0
    per_week: dict[str, float] = defaultdict(float)
    for s in sessions:
        p = prices.get(_norm_model(s.get("model", "")))
        if not p:
            continue  # a model with no pinned price contributes nothing (never estimated)
        c = (int(s.get("input_tokens", 0) or 0) * p.get("input_per_mtok", 0)
             + int(s.get("output_tokens", 0) or 0) * p.get("output_per_mtok", 0)
             + int(s.get("cache_read_tokens", 0) or 0) * p.get("cache_read_per_mtok", 0)
             + int(s.get("cache_creation_tokens", 0) or 0) * p.get("cache_write_per_mtok", 0)) / 1_000_000
        total += c
        if s.get("week"):
            per_week[s["week"]] += c
    base.update({
        "available": True, "total": round(total, 2),
        "pricing_source": pricing.get("source_url"), "as_of": pricing.get("as_of"),
        "trend": [{"week": w, "cost": round(per_week[w], 2)} for w in sorted(per_week)],
    })
    return base


# --- live log readers (metadata/usage only — NEVER transcript text, AD-9) -----
def _iso_week(ts: str) -> str | None:
    try:
        from datetime import date
        d = date.fromisoformat(str(ts)[:10])
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    except Exception:
        return None


def read_claude_sessions(logs_dir: Path) -> list[dict]:
    """Best-effort: from ~/.claude/projects/**/*.jsonl read ONLY usage metadata per session.

    Reads the `usage` token counts and `model` from assistant records; ignores all message content.
    """
    logs_dir = Path(logs_dir).expanduser()
    out: list[dict] = []
    if not logs_dir.exists():
        return out
    for jf in logs_dir.rglob("*.jsonl"):
        agg = {"model": None, "week": None, "input_tokens": 0, "output_tokens": 0,
               "cache_read_tokens": 0, "cache_creation_tokens": 0}
        try:
            for line in jf.read_text(errors="ignore").splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                msg = rec.get("message") or {}
                if msg.get("model"):
                    agg["model"] = msg["model"]
                u = msg.get("usage") or {}
                agg["input_tokens"] += int(u.get("input_tokens", 0) or 0)
                agg["output_tokens"] += int(u.get("output_tokens", 0) or 0)
                agg["cache_read_tokens"] += int(u.get("cache_read_input_tokens", 0) or 0)
                agg["cache_creation_tokens"] += int(u.get("cache_creation_input_tokens", 0) or 0)
                if not agg["week"] and rec.get("timestamp"):
                    agg["week"] = _iso_week(rec["timestamp"])
        except Exception:
            continue
        if agg["model"]:
            out.append(agg)
    return out


def compute(ai_cfg: dict, pricing_cfg: dict, redaction_cfg: dict | None = None) -> dict:
    logs = (ai_cfg or {}).get("logs", {}) or {}
    sessions = read_claude_sessions(Path(logs.get("claude_code", "~/.claude/projects")))
    confounders = ((redaction_cfg or {}).get("controlled_vocabulary", {}) or {}).get("confounders")
    valid = [c for c in _DEFAULT_CONFOUNDERS if not confounders or c in confounders]
    return aggregate_sessions(sessions, pricing_cfg, valid or None)
