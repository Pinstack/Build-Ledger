"""Assembler: tiering, stable ids, id-keyed assembly, derived aggregates, determinism
(Stories 1.3/1.5; AD-13/14/15)."""
import unittest

import contract
from _util import arts, co, metrics, signals
from collect import aggregate, assemble_document, load_config, stable_id, tier

CFG = load_config()


def descriptor(name, public, archived=False, lang="Python"):
    return {"name": name, "nameWithOwner": f"Pinstack/{name}",
            "visibility": "PUBLIC" if public else "PRIVATE", "isArchived": archived,
            "isFork": False, "isMirror": False, "primaryLanguage": {"name": lang},
            "createdAt": "2025-01-01", "pushedAt": "2026-01-01"}


def repo_input(name, public, commits, human, ai_co, agents=(), bots=(), archived=False):
    d = descriptor(name, public, archived)
    return {"descriptor": d, "tiering": tier(d, CFG["repos"], CFG["redaction"]),
            "metrics": metrics(commits=commits, loc_added=commits * 10),
            "signals": signals(True, False, False),
            "coauthorship": co(commits, human, ai_co, agents=agents, bots=bots),
            "ai_artefacts": arts(1, 0, 0), "exclusion_tallies": {"lockfiles": 1}}


class TestTiering(unittest.TestCase):
    def test_private_defaults_to_silhouette(self):
        t = tier(descriptor("x", public=False), CFG["repos"], CFG["redaction"])
        self.assertEqual(t["display_tier"], "aggregate_only")
        self.assertFalse(t["allowlisted"])
        self.assertIsNone(t["label"])

    def test_public_keeps_name(self):
        t = tier(descriptor("meshic", public=True), CFG["repos"], CFG["redaction"])
        self.assertEqual(t["display_tier"], "public")
        self.assertEqual(t["label"], "meshic")

    def test_stable_id_is_deterministic_and_opaque(self):
        self.assertEqual(stable_id("Pinstack/meshic"), stable_id("Pinstack/meshic"))
        self.assertNotIn("meshic", stable_id("Pinstack/meshic"))


class TestAssembly(unittest.TestCase):
    def setUp(self):
        self.inputs = [
            repo_input("pubA", True, 100, 70, 60, agents=[("cursor[bot]", 20)], bots=[("dependabot", 10)]),
            repo_input("privB", False, 50, 50, 25),
            repo_input("privC", False, 10, 9, 0, archived=True),
        ]
        self.doc = assemble_document(self.inputs, exclusion_repo_tallies={"forks": 2, "mirrors": 1},
                                     date_range={"first_commit": "2025-01-01", "latest_commit": "2026-01-01"},
                                     generated_at="2026-06-24T00:00:00Z", cfg=CFG)

    def test_assembled_doc_is_valid(self):
        self.assertEqual(contract.validate(self.doc), [])

    def test_aggregates_reconcile_with_rows(self):
        rows = self.doc["repositories"]
        agg = self.doc["aggregates"]
        self.assertEqual(agg["totals"]["commits"], sum(r["metrics"]["commits"] for r in rows))
        self.assertEqual(agg["totals"]["user_authored_commits"],
                         sum(r["coauthorship"]["human_commits"] for r in rows))
        self.assertEqual(agg["coauthorship"]["ai_coauthored_commits"],
                         sum(r["coauthorship"]["ai_coauthored_commits"] for r in rows))

    def test_repo_counts(self):
        rc = self.doc["aggregates"]["repo_counts"]
        self.assertEqual(rc, {"public": 1, "private": 2, "archived": 1, "active": 2})

    def test_exclusions_summed(self):
        exc = self.doc["exclusions"]
        self.assertEqual(exc["forks"], 2)
        self.assertEqual(exc["mirrors"], 1)
        self.assertEqual(exc["lockfiles"], 3)        # 1 per repo x 3
        self.assertEqual(exc["bot_commits"], 10)     # dependabot from pubA

    def test_empty_allowlist_all_false(self):
        self.assertTrue(all(not r["allowlisted"] for r in self.doc["repositories"]))

    def test_silhouettes_have_no_label(self):
        for r in self.doc["repositories"]:
            if r["display_tier"] == "aggregate_only":
                self.assertNotIn("label", r)

    def test_deterministic_ordering(self):
        d2 = assemble_document(list(reversed(self.inputs)), exclusion_repo_tallies={"forks": 2, "mirrors": 1},
                               date_range={"first_commit": "2025-01-01", "latest_commit": "2026-01-01"},
                               generated_at="2026-06-24T00:00:00Z", cfg=CFG)
        self.assertEqual([r["id"] for r in self.doc["repositories"]],
                         [r["id"] for r in d2["repositories"]])

    def test_typed_empty_modules_present(self):
        self.assertFalse(self.doc["agentic_practice"]["available"])
        self.assertFalse(self.doc["retrospective"]["available"])
        self.assertNotIn("mirror_view", self.doc["retrospective"])
        self.assertFalse(self.doc["in_flight"]["available"])


if __name__ == "__main__":
    unittest.main()
