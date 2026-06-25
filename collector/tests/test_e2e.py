"""End-to-end verification over the committed, converged real-data artifact (Story 1.6).

Proves the published public/build-ledger.json is schema-valid, redaction-safe (clean leak-scan,
no mirror_view, no legacy spike fields), and that every headline aggregate reconciles with the
sum of the repository rows it summarizes (AD-14).
"""
import json
import unittest
from pathlib import Path

import contract
import redaction
from collect import load_config

ROOT = Path(__file__).resolve().parent.parent.parent
DOC = json.loads((ROOT / "public" / "build-ledger.json").read_text())
CFG = load_config()


class TestPublishedArtifact(unittest.TestCase):
    def test_schema_valid(self):
        self.assertEqual(contract.validate(DOC), [])

    def test_redaction_safe(self):
        redaction.assert_safe(DOC, redaction_cfg=CFG["redaction"], ai_cfg=CFG["ai_sources"])

    def test_no_legacy_spike_fields(self):
        self.assertNotEqual(DOC["schema_version"], "build-ledger.v1")  # semver now
        self.assertEqual(DOC["schema_version"], "1.0.0")
        for r in DOC["repositories"]:
            self.assertNotIn("visibility", r)          # -> display_tier
            self.assertNotIn("commits_agent_authored", r.get("coauthorship", {}))
        self.assertIsInstance(DOC["exclusions"], dict)  # counts, not a list

    def test_no_silhouette_leaks_identity(self):
        for r in DOC["repositories"]:
            if r["display_tier"] != "public":
                self.assertNotIn("label", r)
                self.assertNotIn("name", r)
                self.assertNotIn("repo", r)

    def test_aggregates_reconcile(self):
        rows = DOC["repositories"]
        agg = DOC["aggregates"]
        self.assertEqual(agg["totals"]["commits"], sum(r["metrics"]["commits"] for r in rows))
        self.assertEqual(agg["totals"]["user_authored_commits"],
                         sum(r["coauthorship"]["human_commits"] for r in rows))
        self.assertEqual(agg["coauthorship"]["ai_coauthored_commits"],
                         sum(r["coauthorship"]["ai_coauthored_commits"] for r in rows))
        self.assertEqual(agg["repo_counts"]["public"] + agg["repo_counts"]["private"], len(rows))

    def test_headline_share_is_lower_bound_shape(self):
        agg = DOC["aggregates"]["coauthorship"]
        self.assertEqual(agg["unit"], "commit")
        self.assertTrue(0.0 <= agg["ai_coauthored_share"] <= 1.0)
        # the published floor: ~61.4% of commits AI-co-authored, commit-level
        self.assertAlmostEqual(agg["ai_coauthored_share"], 0.614, places=2)

    def test_no_attribution_key_in_v1(self):
        # the forward-compatible line-level representation is reserved for v1.5, not emitted in v1
        for r in DOC["repositories"]:
            self.assertNotIn("attribution", r)


if __name__ == "__main__":
    unittest.main()
