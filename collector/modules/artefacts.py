"""AI-Native Artefact detection + three-class classification (FR-4). Owns repositories[].ai_artefacts.

Detects CLAUDE.md / AGENTS.md / .cursorrules / .claude / mcp(.json) and friends, and assigns each
detected artefact to EXACTLY ONE of the three Artefact Classes. Class precedence is fixed
(workflow_infrastructure > delivery_artefacts > quality_controls) so a path that two classes both
list is counted once, deterministically. Only aggregate per-class counts surface — never a path or
name — so a private repo's artefacts are Silhouette-safe (FR-4, FR-6).
"""
from __future__ import annotations

from pathlib import Path

from contract import ARTEFACT_CLASSES, empty_artefacts

# Fixed precedence: the order classes are tried; first match wins (exactly-one-class guarantee).
_PRECEDENCE = ("workflow_infrastructure", "delivery_artefacts", "quality_controls")


def _class_specs(ai_cfg: dict) -> dict:
    return ai_cfg.get("artefact_classes", {}) or {}


def classify_present(present: set[str], ai_cfg: dict) -> dict:
    """Pure classification: given a set of present artefact identifiers (the configured file/dir
    names that exist in the repo), return per-class counts with exactly-one-class precedence."""
    specs = _class_specs(ai_cfg)
    counts = empty_artefacts()
    seen: set[str] = set()
    for cls in _PRECEDENCE:
        spec = specs.get(cls, {}) or {}
        identifiers = list(spec.get("files", []) or []) + list(spec.get("dirs", []) or [])
        for ident in identifiers:
            if ident in present and ident not in seen:
                counts[cls] += 1
                seen.add(ident)
    return counts


def detect(clone_path: Path, ai_cfg: dict) -> dict:
    """Detect which configured artefacts exist in the clone, then classify them."""
    clone_path = Path(clone_path)
    specs = _class_specs(ai_cfg)
    present: set[str] = set()
    for cls in ARTEFACT_CLASSES:
        spec = specs.get(cls, {}) or {}
        for f in spec.get("files", []) or []:
            if (clone_path / f).is_file():
                present.add(f)
        for d in spec.get("dirs", []) or []:
            if (clone_path / d).is_dir():
                present.add(d)
    return classify_present(present, ai_cfg)
