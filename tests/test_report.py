import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from report import (
    REPORT_DIR,
    REPORT_FILENAME,
    create_quality_report,
    generate_quality_report,
    save_quality_report,
    setup_report,
)


class Report2Tests(unittest.TestCase):
    def test_setup_report_uses_configured_directory_and_filename(self):
        expected_path = Path("/tmp/data_quality.json")

        with patch("report2.create_file_path", return_value=expected_path) as create:
            result = setup_report()

        self.assertEqual(result, expected_path)
        create.assert_called_once_with(
            dirname=REPORT_DIR,
            filename=REPORT_FILENAME,
        )

    def test_report_counts_invalid_records_and_individual_issues(self):
        source = pd.DataFrame({"order_item_id": [1, 2, 3]})
        valid = pd.DataFrame({"order_item_id": [1]})
        issues = pd.DataFrame(
            {
                "order_item_id": [2, 2, 3],
                "issue_type": [
                    "Invalid Quantity",
                    "Invalid Unit Price",
                    "Cancelled Order",
                ],
            }
        )

        result = generate_quality_report(source, valid, issues, inserted_count=2)

        self.assertEqual(
            result,
            {
                "summary": {
                    "total_records": 3,
                    "valid_records": 1,
                    "invalid_records": 2,
                    "issue_count": 3,
                },
                "quality_rates": {
                    "valid_rate": 33.33,
                    "invalid_rate": 66.67,
                },
                "load_statistics": {"inserted_count": 2},
            },
        )

    def test_empty_issue_dataframe_without_columns_is_supported(self):
        result = generate_quality_report(
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            inserted_count=0,
        )

        self.assertEqual(result["summary"]["invalid_records"], 0)
        self.assertEqual(result["summary"]["issue_count"], 0)
        self.assertEqual(result["quality_rates"]["valid_rate"], 0.0)
        self.assertEqual(result["quality_rates"]["invalid_rate"], 0.0)

    def test_rejects_invalid_inserted_counts(self):
        for inserted_count in (-1, 1.5, True):
            with self.subTest(inserted_count=inserted_count):
                with self.assertRaises(ValueError):
                    generate_quality_report(
                        pd.DataFrame(),
                        pd.DataFrame(),
                        pd.DataFrame(),
                        inserted_count,
                    )

    def test_rejects_nonempty_issues_without_order_item_ids(self):
        with self.assertRaisesRegex(ValueError, "order_item_id"):
            generate_quality_report(
                pd.DataFrame({"order_item_id": [1]}),
                pd.DataFrame(),
                pd.DataFrame({"issue_type": ["Invalid Quantity"]}),
                inserted_count=1,
            )

    def test_saves_report_and_create_helper_returns_saved_report(self):
        source = pd.DataFrame({"order_item_id": [1]})
        valid = source.copy()
        issues = pd.DataFrame()

        with TemporaryDirectory() as directory:
            expected_path = Path(directory) / "nested" / "report.json"
            result = create_quality_report(
                source,
                valid,
                issues,
                inserted_count=0,
                output_path=expected_path,
            )

            self.assertTrue(expected_path.exists())
            self.assertEqual(
                json.loads(expected_path.read_text(encoding="utf-8")),
                result,
            )
            self.assertEqual(result["summary"]["total_records"], 1)

    def test_save_rejects_invalid_report_and_path(self):
        with TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"

            with self.assertRaises(ValueError):
                save_quality_report([], output_path)
            with self.assertRaises(ValueError):
                save_quality_report({}, str(output_path))


if __name__ == "__main__":
    unittest.main()
