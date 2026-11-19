import json
import re
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
    def test_setup_report_includes_date_and_run_id_in_filename(self):
        with patch(
            "report.create_file_path",
            side_effect=lambda dirname, filename: (
                Path("/tmp") / dirname / filename
            ),
        ) as create:
            result = setup_report("run-123")

        self.assertEqual(result.parent, Path("/tmp") / REPORT_DIR)
        create.assert_called_once()
        self.assertEqual(create.call_args.kwargs["dirname"], REPORT_DIR)
        filename = create.call_args.kwargs["filename"]
        self.assertRegex(
            filename,
            rf"^{re.escape(Path(REPORT_FILENAME).stem)}_\d{{8}}_run-123"
            rf"{re.escape(Path(REPORT_FILENAME).suffix)}$",
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

    def test_each_run_id_writes_a_separate_report_file(self):
        source = pd.DataFrame({"order_item_id": [1]})

        with TemporaryDirectory() as directory:
            with patch(
                "report.create_file_path",
                side_effect=lambda dirname, filename: (
                    Path(directory) / dirname / filename
                ),
            ):
                first_path = setup_report("run-one")
                create_quality_report(
                    source,
                    source,
                    pd.DataFrame(),
                    inserted_count=0,
                    output_path=first_path,
                )
                first_contents = first_path.read_text(encoding="utf-8")

                second_path = setup_report("run-two")
                create_quality_report(
                    source,
                    source,
                    pd.DataFrame(),
                    inserted_count=0,
                    output_path=second_path,
                )

            self.assertNotEqual(first_path, second_path)
            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())
            self.assertRegex(first_path.name, r"^data_quality_\d{8}_run-one\.json$")
            self.assertRegex(second_path.name, r"^data_quality_\d{8}_run-two\.json$")
            self.assertEqual(
                first_path.read_text(encoding="utf-8"),
                first_contents,
            )

    def test_save_rejects_invalid_report_and_path(self):
        with TemporaryDirectory() as directory:
            output_path = Path(directory) / "report.json"

            with self.assertRaises(ValueError):
                save_quality_report([], output_path)
            with self.assertRaises(ValueError):
                save_quality_report({}, str(output_path))


if __name__ == "__main__":
    unittest.main()
