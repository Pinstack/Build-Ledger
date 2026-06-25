"""Retrospective (Story 4.2): source-bound two framings; mirror_view never in the public object."""
import unittest
from pathlib import Path

from modules import retrospective as retro

ROOT = Path(__file__).resolve().parent.parent.parent


class TestRetrospective(unittest.TestCase):
    def test_window_filters_noise_and_refs_git(self):
        subjects = [("a1b2c3d4e5f6", "Land the redaction gate"),
                    ("ffffffffffff", "Merge branch 'x'"),
                    ("0123456789ab", "wip scratch")]
        view = retro.window_from_git(subjects)
        self.assertEqual(len(view), 1)
        self.assertEqual(view[0]["claim"], "Land the redaction gate")
        self.assertEqual(view[0]["evidence_ref"], "git:a1b2c3d4e5")

    def test_parse_memlog(self):
        text = "# Heading note here\n- a bullet observation\nplain line ignored\n* another bullet"
        notes = retro.parse_memlog(text, "x.memlog.md")
        claims = [n["claim"] for n in notes]
        self.assertIn("a bullet observation", claims)
        self.assertIn("another bullet", claims)
        self.assertTrue(all(n["evidence_ref"] == "memlog:x.memlog.md" for n in notes))

    def test_public_object_never_has_mirror_view(self):
        public, mirror_view, available = retro.compute(ROOT)
        self.assertNotIn("mirror_view", public)            # AD-6: never public
        self.assertIn("window_view", public)
        self.assertIsInstance(mirror_view, list)           # returned separately for the drawer

    def test_meta_retrospective_available_over_this_repo(self):
        public, mirror_view, available = retro.compute(ROOT)
        # this repo has git history + _bmad-output memlogs -> the self-evidencing build retro
        self.assertTrue(available)
        self.assertTrue(len(public["window_view"]) >= 1)


if __name__ == "__main__":
    unittest.main()
