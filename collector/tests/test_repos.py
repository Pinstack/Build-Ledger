"""Repository metrics, signals, and exclusion classification (Story 1.5)."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from collect import load_config
from modules import repos

EXC = load_config()["exclusions"]


class TestExclusions(unittest.TestCase):
    def test_lockfile_bucket(self):
        self.assertEqual(repos.is_excluded_path("package-lock.json", EXC), (True, "lockfiles"))

    def test_vendored_dir_bucket(self):
        self.assertEqual(repos.is_excluded_path("node_modules/x/y.js", EXC), (True, "vendored"))

    def test_generated_build_dir_bucket(self):
        self.assertEqual(repos.is_excluded_path("dist/app.js", EXC), (True, "generated"))

    def test_minified_bucket(self):
        self.assertEqual(repos.is_excluded_path("static/app.min.js", EXC), (True, "minified"))

    def test_source_file_not_excluded(self):
        self.assertEqual(repos.is_excluded_path("src/app.py", EXC), (False, None))


class TestSignals(unittest.TestCase):
    def test_detects_all(self):
        sig = repos.detect_signals(["tests/test_x.py", ".github/workflows/ci.yml", "migrations/001.sql"])
        self.assertTrue(sig["has_tests"] and sig["has_ci"] and sig["has_migrations"])

    def test_none(self):
        sig = repos.detect_signals(["src/app.py", "README.md"])
        self.assertFalse(sig["has_tests"] or sig["has_ci"] or sig["has_migrations"])

    def test_spec_files_count_as_tests(self):
        self.assertTrue(repos.detect_signals(["app/foo.spec.ts"])["has_tests"])


class TestMetricsIntegration(unittest.TestCase):
    def test_metrics_over_real_repo_excludes_lockfile(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                   "HOME": d, "PATH": "/usr/bin:/bin"}
            def git(*a):
                subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, env=env)
            git("init", "-q"); git("config", "user.name", "R"); git("config", "user.email", "r@x")
            (repo / "src").mkdir()
            (repo / "src" / "app.py").write_text("print(1)\n")
            (repo / "package-lock.json").write_text("{}\n")
            (repo / "tests").mkdir(); (repo / "tests" / "test_app.py").write_text("def test(): pass\n")
            git("add", "."); git("commit", "-q", "-m", "init")
            m, sig, tallies = repos.metrics(repo, EXC)
            self.assertEqual(m["commits"], 1)
            self.assertEqual(m["files"], 2)           # app.py + test_app.py; lockfile excluded
            self.assertEqual(tallies.get("lockfiles"), 1)
            self.assertTrue(sig["has_tests"])
            self.assertGreater(m["loc_added"], 0)


if __name__ == "__main__":
    unittest.main()
