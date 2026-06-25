"""Agentic Practice & Efficiency (Story 4.1): aggregate-only, auditable-cost-or-none."""
import unittest

from modules import practice

SESSIONS = [
    {"model": "Claude Opus 4.8", "week": "2026-W20", "input_tokens": 1000, "output_tokens": 200,
     "cache_read_tokens": 9000, "cache_creation_tokens": 0},
    {"model": "Claude Sonnet 4.6", "week": "2026-W20", "input_tokens": 2000, "output_tokens": 400,
     "cache_read_tokens": 8000, "cache_creation_tokens": 0},
    {"model": "Claude Opus 4.8", "week": "2026-W21", "input_tokens": 0, "output_tokens": 0,
     "cache_read_tokens": 0, "cache_creation_tokens": 0},
]


class TestPractice(unittest.TestCase):
    def test_empty_is_unavailable(self):
        self.assertFalse(practice.aggregate_sessions([])["available"])

    def test_cadence_and_model_mix(self):
        ap = practice.aggregate_sessions(SESSIONS)
        self.assertTrue(ap["available"])
        self.assertEqual(ap["cadence"]["sessions"], 3)
        self.assertEqual(ap["cadence"]["weeks_active"], 2)
        top = ap["model_mix"][0]
        self.assertEqual(top["model"], "Claude Opus 4.8")
        self.assertEqual(top["sessions"], 2)
        self.assertAlmostEqual(sum(m["share"] for m in ap["model_mix"]), 1.0, places=2)

    def test_cache_hit_ratio(self):
        ap = practice.aggregate_sessions(SESSIONS)
        # cache_read 17000 / (input 3000 + cache_read 17000 + create 0) = 0.85
        self.assertEqual(ap["cache_hit_ratio"], 0.85)

    def test_cost_omitted_without_pinned_pricing(self):
        ap = practice.aggregate_sessions(SESSIONS, pricing={"prices": {}})
        self.assertFalse(ap["cost"]["available"])
        self.assertIsNone(ap["cost"]["total"])

    def test_cost_computed_with_pinned_pricing(self):
        pricing = {"as_of": "2026-06-01", "source_url": "https://example.com/prices",
                   "prices": {"Claude Opus 4.8": {"input_per_mtok": 15, "output_per_mtok": 75,
                                                   "cache_read_per_mtok": 1.5, "cache_write_per_mtok": 18.75},
                              "Claude Sonnet 4.6": {"input_per_mtok": 3, "output_per_mtok": 15,
                                                    "cache_read_per_mtok": 0.3, "cache_write_per_mtok": 3.75}}}
        ap = practice.aggregate_sessions(SESSIONS, pricing=pricing)
        self.assertTrue(ap["cost"]["available"])
        self.assertGreater(ap["cost"]["total"], 0)
        self.assertEqual(ap["cost"]["as_of"], "2026-06-01")
        self.assertTrue(ap["cost"]["pricing_source"].startswith("http"))

    def test_confounders_are_controlled(self):
        ap = practice.aggregate_sessions(SESSIONS, confounders=["project mix"])
        self.assertEqual(ap["cost"]["confounders"], ["project mix"])


if __name__ == "__main__":
    unittest.main()
