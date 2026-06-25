"""Contract validator (Story 1.2): a good doc passes, malformed docs fail with clear errors."""
import unittest

from _util import valid_doc
import contract


class TestContract(unittest.TestCase):
    def test_valid_doc_passes(self):
        self.assertEqual(contract.validate(valid_doc()), [])
        self.assertTrue(contract.is_valid(valid_doc()))

    def test_missing_top_level_key_fails(self):
        d = valid_doc()
        del d["aggregates"]
        errs = contract.validate(d)
        self.assertTrue(any("aggregates" in e for e in errs))

    def test_schema_version_must_match_metadata(self):
        d = valid_doc()
        d["ledger_metadata"]["schema_version"] = "1.1.0"
        self.assertTrue(any("schema_version" in e for e in contract.validate(d)))

    def test_unsupported_major_fails(self):
        d = valid_doc()
        d["schema_version"] = "2.0.0"
        d["ledger_metadata"]["schema_version"] = "2.0.0"
        self.assertTrue(any("MAJOR" in e for e in contract.validate(d)))

    def test_bad_display_tier_fails(self):
        d = valid_doc()
        d["repositories"][0]["display_tier"] = "secret"
        self.assertTrue(any("display_tier" in e for e in contract.validate(d)))

    def test_public_requires_label(self):
        d = valid_doc()
        del d["repositories"][0]["label"]
        self.assertTrue(any("label required" in e for e in contract.validate(d)))

    def test_aggregate_only_forbids_label(self):
        d = valid_doc()
        d["repositories"][1]["label"] = "Leaky Name"
        self.assertTrue(any("aggregate_only" in e for e in contract.validate(d)))

    def test_coauthorship_unit_must_be_commit(self):
        d = valid_doc()
        d["repositories"][0]["coauthorship"]["unit"] = "line"
        self.assertTrue(any("unit" in e for e in contract.validate(d)))

    def test_mirror_view_present_fails_validation(self):
        d = valid_doc()
        d["retrospective"]["mirror_view"] = []
        self.assertTrue(any("mirror_view" in e for e in contract.validate(d)))

    def test_artefacts_classes_required(self):
        d = valid_doc()
        del d["repositories"][0]["ai_artefacts"]["quality_controls"]
        self.assertTrue(any("ai_artefacts.quality_controls" in e for e in contract.validate(d)))

    def test_bool_is_not_int(self):
        d = valid_doc()
        d["repositories"][0]["metrics"]["commits"] = True  # bool must not satisfy int
        self.assertTrue(any("metrics.commits" in e for e in contract.validate(d)))


if __name__ == "__main__":
    unittest.main()
