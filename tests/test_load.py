import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from etl.load import load_issues


class LoadIssuesTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value

    def test_empty_issues_do_not_open_a_cursor(self):
        issues = pd.DataFrame()

        with patch("etl.load.logging.info") as log_info:
            result = load_issues(self.connection, issues)

        self.assertEqual(result, 0)
        self.connection.cursor.assert_not_called()
        log_info.assert_called_once_with("沒有異常資料需要寫入。")

    def test_inserts_issue_records_and_returns_inserted_count(self):
        issues = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "issue_type": "Invalid Quantity",
                    "issue_description": "Quantity must be greater than zero",
                },
                {
                    "order_item_id": 2,
                    "order_id": 102,
                    "issue_type": "Cancelled Order",
                    "issue_description": "Order has been cancelled",
                },
            ]
        )
        self.cursor.rowcount = 2

        result = load_issues(self.connection, issues)

        self.assertEqual(result, 2)
        self.cursor.executemany.assert_called_once()
        query, records = self.cursor.executemany.call_args.args
        self.assertIn("INSERT INTO public.data_quality_issue_log", query)
        self.assertIn("ON CONFLICT (order_item_id, issue_type)", query)
        self.assertEqual(
            records,
            [
                (
                    1,
                    101,
                    "Invalid Quantity",
                    "Quantity must be greater than zero",
                ),
                (2, 102, "Cancelled Order", "Order has been cancelled"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
