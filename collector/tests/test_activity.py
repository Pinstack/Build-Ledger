"""Activity-over-time aggregation (UX-DR1 chart data)."""
import unittest

from collect import load_config
from modules import activity

EXC = load_config()["exclusions"]


class TestActivity(unittest.TestCase):
    def test_monthly_and_heatmap(self):
        dates = ["2026-01-05", "2026-01-20", "2026-02-02"]
        monthly, heatmap = activity.monthly_and_heatmap(dates)
        self.assertEqual(monthly, {"2026-01": 2, "2026-02": 1})
        self.assertEqual(heatmap["2026-01-05"], 1)

    def test_monthly_loc_excludes_lockfiles(self):
        log = ("\x012026-01-10\n"
               "10\t2\tsrc/app.py\n"
               "500\t0\tpackage-lock.json\n"   # excluded
               "\x012026-02-01\n"
               "3\t1\tsrc/b.py\n")
        loc = activity.monthly_loc(log, EXC)
        self.assertEqual(loc["2026-01"], 8)     # 10-2; lockfile skipped
        self.assertEqual(loc["2026-02"], 2)     # 3-1

    def test_assemble_marks_available(self):
        act = activity.assemble({"2026-01": 2}, {"2026-01": 8}, {"2026-01-05": 2})
        self.assertTrue(act["available"])
        self.assertEqual(act["monthly"], [{"month": "2026-01", "commits": 2, "loc_net": 8}])
        self.assertEqual(act["heatmap"], [{"date": "2026-01-05", "commits": 2}])

    def test_empty_is_unavailable(self):
        self.assertFalse(activity.assemble({}, {}, {})["available"])


if __name__ == "__main__":
    unittest.main()
