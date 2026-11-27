import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from reporting.report_comparison import compare_quality_reports


class ReportComparisonTests(unittest.TestCase):
    def write_report(self, directory, filename, started_at, **overrides):
        report = {
            "processing_time": {"started_at": started_at},
            "summary": {
                "total_records": 10,
                "valid_records": 8,
                "invalid_records": 2,
                "issue_count": 3,
            },
            "quality_rates": {"valid_rate": 80.0, "invalid_rate": 20.0},
            "load_statistics": {"inserted_count": 2},
        }
        report.update(overrides)
        path = Path(directory) / filename
        path.write_text(json.dumps(report), encoding="utf-8")
        return path

    def test_sorts_reports_and_calculates_metric_changes(self):
        with TemporaryDirectory() as directory:
            later = self.write_report(
                directory,
                "later.json",
                "2026-11-25T12:00:00+08:00",
                summary={
                    "total_records": 12,
                    "valid_records": 9,
                    "invalid_records": 3,
                    "issue_count": 4,
                },
                quality_rates={"valid_rate": 75.0, "invalid_rate": 25.0},
                load_statistics={"inserted_count": 1},
            )
            earlier = self.write_report(
                directory,
                "earlier.json",
                "2026-11-25T11:00:00+08:00",
            )

            result = compare_quality_reports([later, earlier])

        self.assertEqual(
            result["report_file"].tolist(),
            ["earlier.json", "later.json"],
        )
        self.assertTrue(pd.isna(result["invalid_records_change"].iloc[0]))
        self.assertEqual(result["invalid_records_change"].iloc[1], 1)
        self.assertEqual(result["valid_rate_change"].iloc[1], -5.0)
        self.assertEqual(result["inserted_count_change"].iloc[1], -1)

    def test_requires_at_least_two_reports(self):
        with self.assertRaisesRegex(ValueError, "At least two"):
            compare_quality_reports([])

    def test_rejects_report_without_timezone(self):
        with TemporaryDirectory() as directory:
            first = self.write_report(
                directory, "first.json", "2026-11-25T11:00:00"
            )
            second = self.write_report(
                directory, "second.json", "2026-11-25T12:00:00+08:00"
            )

            with self.assertRaisesRegex(ValueError, "timezone"):
                compare_quality_reports([first, second])

    def test_skips_report_without_run_timestamp(self):
        with TemporaryDirectory() as directory:
            first = self.write_report(
                directory, "first.json", "2026-11-25T11:00:00+08:00"
            )
            second = self.write_report(
                directory, "second.json", "2026-11-25T12:00:00+08:00"
            )
            report = json.loads(second.read_text(encoding="utf-8"))
            del report["processing_time"]
            second.write_text(json.dumps(report), encoding="utf-8")

            with self.assertLogs(level="WARNING"):
                with self.assertRaisesRegex(ValueError, "At least two reports"):
                    compare_quality_reports([first, second])

    def test_falls_back_to_report_time(self):
        with TemporaryDirectory() as directory:
            first = self.write_report(
                directory, "first.json", "2026-11-25T11:00:00+08:00"
            )
            second = self.write_report(
                directory, "second.json", "2026-11-25T12:00:00+08:00"
            )
            report = json.loads(second.read_text(encoding="utf-8"))
            del report["processing_time"]
            report["report_time"] = {
                "started_at": "2026-11-25T12:00:00+08:00"
            }
            second.write_text(json.dumps(report), encoding="utf-8")

            result = compare_quality_reports([first, second])

        self.assertEqual(
            result["report_file"].tolist(),
            ["first.json", "second.json"],
        )


if __name__ == "__main__":
    unittest.main()
