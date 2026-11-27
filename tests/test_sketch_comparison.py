import json
import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from reporting.sketch_comparison import compare_reports


class SketchComparisonTests(unittest.TestCase):
    def write_report(self, directory, filename, report):
        path = Path(directory) / filename
        path.write_text(json.dumps(report), encoding="utf-8")
        return path

    def report(self, timestamp):
        return {
            "report_time": {"started_at": timestamp},
            "summary": {
                "total_records": 10,
                "valid_records": 8,
                "invalid_records": 2,
                "issue_count": 3,
            },
            "quality_rates": {"valid_rate": 80.0, "invalid_rate": 20.0},
            "load_statistics": {"inserted_count": 1},
        }

    def test_uses_report_time_when_processing_time_is_missing(self):
        with TemporaryDirectory() as directory:
            self.write_report(
                directory,
                "data_quality_first.json",
                self.report("2026-11-25T10:00:00+08:00"),
            )
            later = self.report("2026-11-25T11:00:00+08:00")
            later["summary"]["invalid_records"] = 4
            self.write_report(directory, "data_quality_second.json", later)

            result = compare_reports(Path(directory))

        self.assertTrue(math.isnan(result["invalid_change"].iloc[0]))
        self.assertEqual(result["invalid_change"].iloc[1], 2)

    def test_skips_reports_without_either_timestamp(self):
        with TemporaryDirectory() as directory:
            self.write_report(
                directory, "data_quality_first.json", self.report(None)
            )
            second = self.report("2026-11-25T11:00:00+08:00")
            self.write_report(directory, "data_quality_second.json", second)

            with self.assertRaisesRegex(ValueError, "至少需要兩份"):
                compare_reports(Path(directory))


if __name__ == "__main__":
    unittest.main()
