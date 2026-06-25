#!/usr/bin/env python3
"""Validate a build-ledger.json against the documented contract (Story 1.2).

Usage:
    python3 validate.py [path/to/build-ledger.json] [--redaction]

Exit code 0 = valid (and, with --redaction, redaction-safe); non-zero otherwise. With --redaction
the whole-document fail-closed redaction assert is also run, using the collector's config.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract  # noqa: E402
import redaction  # noqa: E402
from collect import load_config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "public" / "build-ledger.json"


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    path = Path(args[0]) if args else DEFAULT

    if not path.exists():
        print(f"FAIL: no such file: {path}")
        return 2
    try:
        doc = json.loads(path.read_text())
    except Exception as e:
        print(f"FAIL: not valid JSON: {e}")
        return 2

    errors = contract.validate(doc)
    if errors:
        print(f"INVALID: {path} ({len(errors)} error(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"VALID: {path} conforms to schema_version {doc.get('schema_version')}")

    if "--redaction" in flags:
        cfg = load_config()
        try:
            redaction.assert_safe(doc, redaction_cfg=cfg.get("redaction", {}), ai_cfg=cfg.get("ai_sources", {}))
            print("REDACTION-SAFE: whole-document assert passed (fail-closed)")
        except redaction.RedactionError as e:
            print(f"REDACTION FAILURE: {e}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
