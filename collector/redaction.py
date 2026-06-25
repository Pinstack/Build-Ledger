"""Central, fail-closed, whole-document redaction (FR-6, AD-4, AD-6). SAFETY-CRITICAL.

A single pass asserts over the ENTIRE assembled public document, before publish, that none of the
prohibited fields can appear. If any assertion fails the run does NOT publish (fail-closed) — the
caller leaves the previous file intact.

Three layers, defense-in-depth, in order of strength:
  1. Construction  — Silhouettes carry only typed metrics/signals/aggregate counts; risky free-text
                     fields are restricted to a controlled vocabulary by the producing Modules.
  2. Structural    — every non-public repo is asserted to carry no identifying field (name/path/label);
                     `mirror_view` is asserted absent anywhere (AD-6).
  3. Backstop      — a denylist of real private repo / client names (local-only, AD-5) and generic
                     secret-shaped patterns are scanned over every string in the document, to catch
                     anything the first two layers missed. A denylist cannot catch a *novel* client
                     name — which is exactly why layers 1 and 2 are the primary guarantee and this is
                     only the net beneath them.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator

import yaml


class RedactionError(AssertionError):
    """Raised when the whole-document redaction assert fails. Publication must abort (fail-closed)."""


# --- denylist (local-only, outside the repo tree per AD-5) -------------------
def load_denylist(redaction_cfg: dict) -> set[str]:
    """Load the sensitive-token denylist from the local-only file referenced by redaction.yml.

    Returns a lowercased token set. Absent (e.g. on a public CI box that has no private data) ->
    empty set; layers 1 and 2 still hold, and there is no private data present to leak anyway.
    """
    ref = (redaction_cfg or {}).get("denylist_file")
    if not ref:
        return set()
    path = Path(ref).expanduser()
    if not path.exists():
        return set()
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except Exception:
        # A malformed denylist must not silently disable the backstop.
        raise RedactionError(f"denylist file present but unreadable: {path}")
    tokens: set[str] = set()
    for key in ("repo_names", "client_names", "tokens", "proprietary_names"):
        for t in (data.get(key) or []):
            if isinstance(t, str) and t.strip():
                tokens.add(t.strip().lower())
    return tokens


# --- document walk ------------------------------------------------------------
def _walk(obj, path: str = "$") -> Iterator[tuple[str, str, object]]:
    """Yield (json_path, key, value) for every node, so callers can scan keys and string values."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            yield (p, k, v)
            yield from _walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}[{i}]"
            yield (p, None, v)
            yield from _walk(v, p)


def _strings(obj) -> Iterator[tuple[str, str]]:
    for p, _k, v in _walk(obj):
        if isinstance(v, str):
            yield (p, v)


# --- controlled vocabulary ----------------------------------------------------
_MODEL_NAME_RE = re.compile(
    r"^(Claude|GPT|OpenAI|Cursor|Gemini|Llama|Mistral|Codex|Fable|Opus|Sonnet|Haiku|o\d)\b",
    re.I,
)


def _allowed_authors(ai_cfg: dict) -> set[str]:
    return set(ai_cfg.get("agents", [])) | set(ai_cfg.get("bots", [])) | {"Other agent", "Other bot"}


# --- the assert ---------------------------------------------------------------
def assert_safe(doc: dict, *, redaction_cfg: dict, ai_cfg: dict, denylist: set[str] | None = None) -> None:
    """Whole-document fail-closed assert. Raises RedactionError on the first violation; mutates nothing."""
    if denylist is None:
        denylist = load_denylist(redaction_cfg)

    vocab = (redaction_cfg or {}).get("controlled_vocabulary", {}) or {}
    allowed_langs = set(vocab.get("languages", [])) | {"Other"}
    allowed_confounders = set(vocab.get("confounders", []))
    generic_category = vocab.get("generic_repo_category", "Private software system")
    allowed_authors = _allowed_authors(ai_cfg or {})
    secret_res = [re.compile(p) for p in (redaction_cfg or {}).get("secret_patterns", [])]

    # Layer 2a — mirror_view must never appear anywhere (AD-6).
    for p, k, _v in _walk(doc):
        if k == "mirror_view":
            raise RedactionError(f"mirror_view present at {p} — the Mirror View must never publish (AD-6)")

    # Layer 2b — per-repo structural silhouette guarantee.
    forbidden_repo_keys = {"name", "repo", "full_name", "nameWithOwner", "path", "url",
                           "clone_url", "ssh_url", "homepage", "owner"}
    for i, r in enumerate(doc.get("repositories", []) or []):
        if not isinstance(r, dict):
            continue
        at = f"repositories[{i}]"
        tier = r.get("display_tier")
        leaked = forbidden_repo_keys & set(r.keys())
        if leaked:
            raise RedactionError(f"{at}: forbidden identifying key(s) {sorted(leaked)} present")
        if tier != "public":
            # A non-public repo may rise above aggregate_only ONLY via the Allowlist.
            if tier == "aggregate_only":
                if r.get("label") not in (None, "") or ("label" in r and r["label"]):
                    raise RedactionError(f"{at}: aggregate_only Silhouette must carry no label")
            elif tier == "redacted":
                if not r.get("allowlisted"):
                    raise RedactionError(f"{at}: redacted tier requires allowlisted=true (Allowlist is the only promotion path)")
                if r.get("label") != generic_category and not _label_is_generic(r.get("label")):
                    raise RedactionError(f"{at}: redacted label must be a generic category, got {r.get('label')!r}")
            else:
                raise RedactionError(f"{at}: invalid non-public display_tier {tier!r}")
        # coauthorship authors must be controlled-vocabulary tool identities (no human/client names).
        co = r.get("coauthorship") or {}
        for key in ("agents", "excluded_bots"):
            for a in co.get(key, []) or []:
                author = (a or {}).get("author")
                if author not in allowed_authors:
                    raise RedactionError(
                        f"{at}.coauthorship.{key}: author {author!r} not in controlled vocabulary")

    # Layer 2c — aggregate free-text fields restricted to controlled vocabulary.
    for j, l in enumerate(((doc.get("aggregates") or {}).get("languages") or [])):
        name = (l or {}).get("name")
        if name not in allowed_langs:
            raise RedactionError(f"aggregates.languages[{j}].name {name!r} not in controlled vocabulary")

    ap = doc.get("agentic_practice") or {}
    for c in ((ap.get("cost") or {}).get("confounders") or []):
        if c not in allowed_confounders:
            raise RedactionError(f"agentic_practice.cost.confounders entry {c!r} not in controlled vocabulary")
    for m in (ap.get("model_mix") or []):
        name = (m or {}).get("model") if isinstance(m, dict) else None
        if name is not None and name not in allowed_authors and not _MODEL_NAME_RE.match(str(name)):
            raise RedactionError(f"agentic_practice.model_mix model {name!r} not a recognised model identity")

    # Layer 3 — denylist + secret-pattern backstop over EVERY string in the document.
    for p, s in _strings(doc):
        low = s.lower()
        for tok in denylist:
            if tok and tok in low:
                raise RedactionError(f"denylisted token detected at {p}")  # never echo the token itself
        for rx in secret_res:
            if rx.search(s):
                raise RedactionError(f"secret-shaped pattern detected at {p}")


def _label_is_generic(label) -> bool:
    """A redacted label is generic if it carries no specific identifier (letters+spaces, no digits/paths)."""
    if not isinstance(label, str) or not label:
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z \-/&]*", label))


def is_safe(doc: dict, *, redaction_cfg: dict, ai_cfg: dict, denylist: set[str] | None = None) -> bool:
    try:
        assert_safe(doc, redaction_cfg=redaction_cfg, ai_cfg=ai_cfg, denylist=denylist)
        return True
    except RedactionError:
        return False
