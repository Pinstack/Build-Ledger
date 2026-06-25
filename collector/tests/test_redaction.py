"""SAFETY-CRITICAL: the whole-document, fail-closed redaction assert (FR-6, AD-4, AD-6).

Exercises the synthetic-private-repo fixture across all five public blocks and proves every leak
vector is caught fail-closed, while a clean document passes.
"""
import copy
import unittest

from _util import valid_doc
import redaction
from collect import load_config

CFG = load_config()
RCFG, AICFG = CFG["redaction"], CFG["ai_sources"]


def assert_doc(doc, denylist=None):
    redaction.assert_safe(doc, redaction_cfg=RCFG, ai_cfg=AICFG, denylist=denylist or set())


class TestRedaction(unittest.TestCase):
    def test_clean_document_passes(self):
        assert_doc(valid_doc())  # all five public blocks present, nothing prohibited

    def test_mirror_view_anywhere_is_caught(self):
        d = valid_doc()
        d["retrospective"]["mirror_view"] = [{"claim": "brutal honesty"}]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_mirror_view_nested_is_caught(self):
        d = valid_doc()
        d["aggregates"]["mirror_view"] = "x"  # even buried deep
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_silhouette_with_name_key_is_caught(self):
        d = valid_doc()
        d["repositories"][1]["name"] = "secret-client-repo"
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_silhouette_with_path_key_is_caught(self):
        d = valid_doc()
        d["repositories"][1]["path"] = "/Users/x/Projects/clientco"
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_silhouette_with_label_is_caught(self):
        d = valid_doc()
        d["repositories"][1]["label"] = "ClientCo Platform"
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_redacted_tier_requires_allowlist(self):
        d = valid_doc()
        d["repositories"][1]["display_tier"] = "redacted"
        d["repositories"][1]["label"] = "Private software system"
        d["repositories"][1]["allowlisted"] = False  # promotion without allowlist -> fail
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_non_vocabulary_agent_author_is_caught(self):
        # a human/client name smuggled into agents[] must be rejected (controlled vocabulary)
        d = valid_doc()
        d["repositories"][0]["coauthorship"]["agents"] = [{"author": "Jane From ClientCo", "commits": 3}]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_non_vocabulary_language_is_caught(self):
        d = valid_doc()
        d["aggregates"]["languages"] = [{"name": "ClientProprietaryLang", "share": 1.0}]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_non_vocabulary_confounder_is_caught(self):
        d = valid_doc()
        d["agentic_practice"]["cost"]["confounders"] = ["the ClientCo migration project"]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_secret_pattern_is_caught(self):
        d = valid_doc()
        d["retrospective"]["window_view"] = [{"claim": "api_key=ABCDEF set in config", "evidence_ref": "x"}]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_github_token_pattern_is_caught(self):
        d = valid_doc()
        d["ledger_metadata"]["data_url"] = "ghp_" + "a" * 36
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d)

    def test_denylist_token_is_caught_anywhere(self):
        # the local-only backstop: a known client name appearing in free prose is caught
        d = valid_doc()
        d["retrospective"]["window_view"] = [{"claim": "Delivered the Acme Corp data platform",
                                              "evidence_ref": "memlog"}]
        with self.assertRaises(redaction.RedactionError):
            assert_doc(d, denylist={"acme corp"})

    def test_denylist_clean_when_token_absent(self):
        assert_doc(valid_doc(), denylist={"acme corp"})  # token not present -> passes

    def test_error_message_never_echoes_denylist_token(self):
        d = valid_doc()
        d["repositories"][1] = copy.deepcopy(d["repositories"][1])
        d["aggregates"]["languages"][0]["name"] = "Python"
        d["retrospective"]["window_view"] = [{"claim": "Acme Corp secret thing", "evidence_ref": "x"}]
        try:
            assert_doc(d, denylist={"acme corp"})
            self.fail("expected RedactionError")
        except redaction.RedactionError as e:
            self.assertNotIn("acme corp", str(e).lower())  # never leak the token via the error


if __name__ == "__main__":
    unittest.main()
