"""AI-Native Artefact detection + three-class classification (Story 2.2)."""
import tempfile
import unittest
from pathlib import Path

from collect import load_config
from modules import artefacts

AI = load_config()["ai_sources"]


class TestArtefacts(unittest.TestCase):
    def test_each_artefact_one_class(self):
        present = {"CLAUDE.md", "AGENTS.md", ".claude", "_bmad-output", "evals"}
        counts = artefacts.classify_present(present, AI)
        # CLAUDE.md, AGENTS.md, .claude -> workflow_infrastructure (3)
        self.assertEqual(counts["workflow_infrastructure"], 3)
        self.assertEqual(counts["delivery_artefacts"], 1)   # _bmad-output
        self.assertEqual(counts["quality_controls"], 1)     # evals

    def test_total_equals_distinct_present(self):
        present = {"CLAUDE.md", ".cursorrules", "specs"}
        counts = artefacts.classify_present(present, AI)
        self.assertEqual(sum(counts.values()), 3)

    def test_empty_when_none_present(self):
        self.assertEqual(sum(artefacts.classify_present(set(), AI).values()), 0)

    def test_detect_over_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "CLAUDE.md").write_text("# agent rules")
            (root / ".claude").mkdir()
            (root / "_bmad-output").mkdir()
            counts = artefacts.detect(root, AI)
            self.assertEqual(counts["workflow_infrastructure"], 2)  # CLAUDE.md + .claude
            self.assertEqual(counts["delivery_artefacts"], 1)       # _bmad-output
            self.assertEqual(counts["quality_controls"], 0)


if __name__ == "__main__":
    unittest.main()
