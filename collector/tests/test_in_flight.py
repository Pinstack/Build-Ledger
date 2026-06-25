"""In-Flight (Story 4.3): auditable live signals, aggregate counts only."""
import unittest

from modules import in_flight


class TestInFlight(unittest.TestCase):
    def test_wip_branch_count_excludes_mainlines(self):
        lines = ["main", "develop", "feature/x", "fix/y", "origin/main", "origin/feature/x", "HEAD -> main"]
        # non-mainline by leaf name: feature/x, fix/y, origin/feature/x -> 3 (origin/main excluded, arrow excluded)
        self.assertEqual(in_flight.count_wip_branches(lines), 3)

    def test_trajectory_buckets_recent_weeks(self):
        dates = ["2026-06-01", "2026-06-02", "2026-06-20", "2020-01-01"]
        traj = in_flight.trajectory_from_dates(dates, weeks=4, today="2026-06-22")
        self.assertEqual(len(traj), 4)
        self.assertEqual(sum(traj), 3)        # the 2020 date is outside the trailing window
        self.assertEqual(traj[-1], 1)         # 2026-06-20 in the latest week

    def test_todo_fixme_counts_lines_only(self):
        grep = "a/b.py:12: TODO fix\nc/d.py:3: FIXME later\n"
        self.assertEqual(in_flight.count_todo_fixme(grep), 2)

    def test_empty_clone_list_is_unavailable(self):
        self.assertFalse(in_flight.compute([])["available"])


if __name__ == "__main__":
    unittest.main()
