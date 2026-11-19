import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from report import (
    REPORT_DIR,
    REPORT_FILENAME,
    generate_quality_report,
    save_quality_report,
    setup_report,
)


class ReportTests(unittest.TestCase):
    def test_setup_report_uses_configured_directory_and_filename(self):
        expected_path = Path("/tmp/data_quality.json")

        with patch("report.create_file_path", return_value=expected_path) as create:
            result = setup_report()

        self.assertEqual(result, expected_path)
        create.assert_called_once_with(
            dirname=REPORT_DIR,
            filename=REPORT_FILENAME,
        )

    def test_generates_report_with_rates_rounded_to_two_decimal_places(self):
        result = generate_quality_report(
            total_records=7,
            valid_records=5,
            invalid_records=2,
        )

        self.assertEqual(
            result,
            {
                "total_records": 7,
                "valid_records": 5,
                "invalid_records": 2,
                "valid_rate": 71.43,
                "invalid_rate": 28.57,
            },
        )

    def test_empty_dataset_has_zero_rates(self):
        result = generate_quality_report(0, 0, 0)

        self.assertEqual(result["valid_rate"], 0.0)
        self.assertEqual(result["invalid_rate"], 0.0)

    def test_rejects_negative_counts_and_mismatched_totals(self):
        invalid_counts = (
            (-1, 0, 0),
            (1, -1, 2),
            (1, 2, -1),
            (3, 1, 1),
        )

        for counts in invalid_counts:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                generate_quality_report(*counts)

    def test_rejects_non_integer_counts_and_booleans(self):
        invalid_counts = (
            (1.5, 1, 0.5),
            (1, 0.5, 0),
            (1, 1, 0.0),
            (True, 1, 0),
            (1, False, 1),
            (1, 1, False),
        )

        for counts in invalid_counts:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                generate_quality_report(*counts)

    def test_saves_json_report_as_utf8(self):
        report_data = {"status": "完成", "total_records": 2}

        with TemporaryDirectory() as directory:
            output_path = Path(directory) / "data_quality.json"

            save_quality_report(report_data, output_path)

            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                report_data,
            )
            self.assertIn("完成", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
