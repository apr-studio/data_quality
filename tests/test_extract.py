import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from etl.extract import extract_orders


class ExtractOrdersTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.cursor.description = [
            SimpleNamespace(name="order_item_id"),
            SimpleNamespace(name="order_id"),
            SimpleNamespace(name="unit_price"),
            SimpleNamespace(name="quantity"),
            SimpleNamespace(name="status"),
        ]

    def test_extracts_rows_with_database_column_names(self):
        self.cursor.fetchall.return_value = [
            (2, 102, 3.5, 1, "Completed"),
            (1, 101, 2.0, 4, "Completed"),
        ]

        result = extract_orders(self.connection)

        self.assertEqual(
            result.columns.tolist(),
            ["order_item_id", "order_id", "unit_price", "quantity", "status"],
        )
        self.assertEqual(
            result.to_dict("records"),
            [
                {
                    "order_item_id": 2,
                    "order_id": 102,
                    "unit_price": 3.5,
                    "quantity": 1,
                    "status": "Completed",
                },
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": 2.0,
                    "quantity": 4,
                    "status": "Completed",
                },
            ],
        )

    def test_extracts_empty_result_with_database_columns(self):
        self.cursor.fetchall.return_value = []

        result = extract_orders(self.connection)

        self.assertTrue(result.empty)
        self.assertEqual(
            result.columns.tolist(),
            ["order_item_id", "order_id", "unit_price", "quantity", "status"],
        )

    def test_queries_orders_in_item_id_order(self):
        self.cursor.fetchall.return_value = []

        extract_orders(self.connection)

        self.cursor.execute.assert_called_once()
        query = self.cursor.execute.call_args.args[0]
        self.assertIn("FROM public.orders", query)
        for column in (
            "order_item_id",
            "order_id",
            "unit_price",
            "quantity",
            "status",
        ):
            self.assertIn(column, query)
        self.assertIn("ORDER BY order_item_id", query)


if __name__ == "__main__":
    unittest.main()
