"""Co-Authorship Split (Story 2.1): author classification, controlled-vocab bucketing, trailer
counting, and the reconcilable headline denominator — pure parsers plus a real-git integration."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from _util import COLLECTOR_DIR  # noqa: F401  (ensures sys.path)
from collect import load_config
from modules import coauthorship as ca

AI = load_config()["ai_sources"]


class TestParsers(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(ca.classify_author("cursor[bot]", "x@x", AI), "agent")
        self.assertEqual(ca.classify_author("Cursor Agent", "x@x", AI), "agent")
        self.assertEqual(ca.classify_author("dependabot[bot]", "x@x", AI), "bot")
        self.assertEqual(ca.classify_author("Raedmund", "r@x", AI), "human")
        # an unknown "[bot]" identity is bot-noise, never a genuine agent
        self.assertEqual(ca.classify_author("weird[bot]", "x@x", AI), "bot")

    def test_parse_authors_buckets_and_counts(self):
        shortlog = ("  1390\tRaedmund <r@x.com>\n"
                    "    45\tcursor[bot] <bot@cursor.com>\n"
                    "     1\tCursor Agent <a@cursor.com>\n"
                    "    59\tdependabot[bot] <dep@github.com>\n")
        out = ca.parse_authors(shortlog, AI)
        self.assertEqual(out["human_commits"], 1390)
        self.assertEqual(out["agent_authored_commits"], 46)
        self.assertEqual(out["bot_commits"], 59)
        agents = {a["author"]: a["commits"] for a in out["agents"]}
        self.assertEqual(agents.get("cursor[bot]"), 45)
        self.assertEqual(agents.get("Cursor Agent"), 1)
        bots = {b["author"]: b["commits"] for b in out["excluded_bots"]}
        # canonicalised to the controlled-vocabulary form
        self.assertEqual(bots.get("dependabot"), 59)

    def test_unknown_human_never_becomes_agent(self):
        out = ca.parse_authors("   3\tJane Client <jane@clientco.com>\n", AI)
        self.assertEqual(out["human_commits"], 3)
        self.assertEqual(out["agents"], [])

    def test_count_ai_coauthored_trailers(self):
        bodies = ("h1\x01feat\n\nCo-authored-by: Claude <c@anthropic.com>\x02"
                  "h2\x01fix\n\nCo-authored-by: Jane <j@x.com>\x02"
                  "h3\x01chore\n\nCo-authored-by: cursor[bot] <b@cursor.com>\x02")
        # h1 (Claude) + h3 (cursor) name agents; h2 (Jane) does not
        self.assertEqual(ca.count_ai_coauthored(bodies, AI), 2)

    def test_assemble_denominator_is_all_commits(self):
        authors = {"human_commits": 90, "agent_authored_commits": 5, "bot_commits": 5,
                   "agents": [{"author": "cursor[bot]", "commits": 5}],
                   "excluded_bots": [{"author": "dependabot", "commits": 5}]}
        block = ca.assemble(authors, ai_coauthored=60)
        self.assertEqual(block["total_commits"], 100)        # 90 + 5 + 5
        self.assertEqual(block["ai_coauthored_share"], 0.6)  # 60 / 100
        self.assertEqual(block["unit"], "commit")


class TestGitIntegration(unittest.TestCase):
    def test_compute_over_real_repo(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            def git(*a):
                subprocess.run(["git", "-C", str(repo), *a], check=True,
                               capture_output=True, env={"GIT_CONFIG_GLOBAL": "/dev/null",
                                                         "GIT_CONFIG_SYSTEM": "/dev/null",
                                                         "HOME": d, "PATH": "/usr/bin:/bin"})
            git("init", "-q")
            git("config", "user.name", "Raedmund")
            git("config", "user.email", "r@x.com")
            (repo / "a.txt").write_text("1\n")
            git("add", "."); git("commit", "-q", "-m", "feat\n\nCo-authored-by: Claude <c@anthropic.com>")
            (repo / "b.txt").write_text("2\n")
            git("add", "."); git("commit", "-q", "-m", "plain commit")
            block = ca.compute(repo, AI)
            self.assertEqual(block["total_commits"], 2)
            self.assertEqual(block["human_commits"], 2)
            self.assertEqual(block["ai_coauthored_commits"], 1)
            self.assertEqual(block["ai_coauthored_share"], 0.5)


if __name__ == "__main__":
    unittest.main()
