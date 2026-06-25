"""Retrospective in two framings (FR-11, AD-6). Owns the public top-level `retrospective` key
(window_view ONLY) and the private mirror_view (which goes to the out-of-tree drawer, never public).

Every claim traces to a memlog entry or git evidence — nothing free-authored. The curated Window
View (confident, no self-flagellation, no private specifics) publishes; the brutally-honest Mirror
View is returned separately for the caller to write to ~/.build-ledger/private/mirror.json only.
The published document carries no `retrospective.mirror_view` key (machine-checked by redaction).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from contract import empty_retrospective

# Commit subjects that are noise rather than narrative.
_NOISE = re.compile(r"^(merge|wip|fixup|squash|amend|typo|lint|format|bump|chore\(deps\))\b", re.I)


def window_from_git(subjects: list[tuple[str, str]], limit: int = 12) -> list[dict]:
    """Curated Window View from git commit subjects (public, already-curated, source-bound)."""
    view: list[dict] = []
    for sha, subject in subjects:
        s = subject.strip()
        if not s or _NOISE.match(s):
            continue
        view.append({"claim": s, "evidence_ref": f"git:{sha[:10]}"})
        if len(view) >= limit:
            break
    return view


def parse_memlog(text: str, source: str) -> list[dict]:
    """Extract bullet/heading notes from a BMAD .memlog.md as source-bound entries (no free-authoring)."""
    notes: list[dict] = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*]|#{1,4})\s+(.*\S)", line)
        if m:
            note = m.group(1).strip().lstrip("#").strip()
            if len(note) > 6:
                notes.append({"claim": note, "evidence_ref": f"memlog:{source}"})
    return notes


def mirror_from(memlog_notes: list[dict], window: list[dict], limit: int = 40) -> list[dict]:
    """Brutally-honest Mirror View: the memlog notes (the rough planning record) plus the git
    narrative. Private-only — written to the drawer, never published."""
    return (memlog_notes + window)[:limit]


# --- live path ----------------------------------------------------------------
def _git_subjects(repo_root: Path, limit: int = 40) -> list[tuple[str, str]]:
    try:
        out = subprocess.run(["git", "-C", str(repo_root), "log", "--no-merges",
                              f"-{limit}", "--pretty=format:%H\x1f%s"],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return []
    pairs = []
    for line in out.splitlines():
        if "\x1f" in line:
            sha, subj = line.split("\x1f", 1)
            pairs.append((sha, subj))
    return pairs


def compute(repo_root: Path, memlog_glob: str = "_bmad-output/**/.memlog.md") -> tuple[dict, list[dict], bool]:
    """Return (public_retrospective, mirror_view, available)."""
    repo_root = Path(repo_root)
    subjects = _git_subjects(repo_root)
    window = window_from_git(subjects)

    memlog_notes: list[dict] = []
    for mf in repo_root.glob(memlog_glob):
        try:
            memlog_notes.extend(parse_memlog(mf.read_text(errors="ignore"), mf.name))
        except Exception:
            continue

    retro = empty_retrospective()
    available = bool(window or memlog_notes)
    retro["available"] = available
    retro["window_view"] = window
    mirror_view = mirror_from(memlog_notes, window)
    return retro, mirror_view, available
