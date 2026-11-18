import unittest

import pandas as pd

from transform import transform_orders


class TransformOrdersTests(unittest.TestCase):
    def test_missing_quantity_is_reported_as_invalid(self):
        orders = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": 12.5,
                    "quantity": pd.NA,
                    "status": "Completed",
                }
            ]
        )
        orders["quantity"] = orders["quantity"].astype("Int64")

        valid_orders, issues = transform_orders(orders)

        self.assertTrue(valid_orders.empty)
        self.assertEqual(
            issues[
                ["order_item_id", "issue_type", "issue_description"]
            ].to_dict("records"),
            [
                {
                    "order_item_id": 1,
                    "issue_type": "Invalid Quantity",
                    "issue_description": "Quantity must be present and greater than zero",
                }
            ],
        )

    def test_zero_and_negative_quantities_are_reported(self):
        orders = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": 12.5,
                    "quantity": 0,
                    "status": "Completed",
                },
                {
                    "order_item_id": 2,
                    "order_id": 102,
                    "unit_price": 12.5,
                    "quantity": -1,
                    "status": "Completed",
                },
            ]
        )

        valid_orders, issues = transform_orders(orders)

        self.assertTrue(valid_orders.empty)
        self.assertEqual(
            issues["order_item_id"].tolist(),
            [1, 2],
        )
        self.assertEqual(
            issues["issue_type"].tolist(),
            ["Invalid Quantity", "Invalid Quantity"],
        )

    def test_missing_price_and_cancelled_order_are_reported(self):
        orders = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": None,
                    "quantity": 2,
                    "status": "Completed",
                },
                {
                    "order_item_id": 2,
                    "order_id": 102,
                    "unit_price": 12.5,
                    "quantity": 1,
                    "status": "Cancelled",
                },
            ]
        )

        valid_orders, issues = transform_orders(orders)

        self.assertTrue(valid_orders.empty)
        self.assertEqual(
            set(zip(issues["order_item_id"], issues["issue_type"])),
            {
                (1, "Missing Unit Price"),
                (2, "Cancelled Order"),
            },
        )

    def test_negative_price_is_reported_and_zero_price_is_valid(self):
        orders = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": -1.0,
                    "quantity": 2,
                    "status": "Completed",
                },
                {
                    "order_item_id": 2,
                    "order_id": 102,
                    "unit_price": 0.0,
                    "quantity": 2,
                    "status": "Completed",
                },
            ]
        )

        valid_orders, issues = transform_orders(orders)

        self.assertEqual(valid_orders["order_item_id"].tolist(), [2])
        self.assertEqual(valid_orders["revenue"].tolist(), [0.0])
        self.assertEqual(
            issues[
                ["order_item_id", "issue_type", "issue_description"]
            ].to_dict("records"),
            [
                {
                    "order_item_id": 1,
                    "issue_type": "Invalid Unit Price",
                    "issue_description": "Unit price must not be negative",
                }
            ],
        )

    def test_completed_order_with_valid_fields_has_revenue(self):
        orders = pd.DataFrame(
            [
                {
                    "order_item_id": 1,
                    "order_id": 101,
                    "unit_price": 12.5,
                    "quantity": 2,
                    "status": "Completed",
                }
            ]
        )

        valid_orders, issues = transform_orders(orders)

        self.assertEqual(valid_orders["order_item_id"].tolist(), [1])
        self.assertEqual(valid_orders["revenue"].tolist(), [25.0])
        self.assertTrue(issues.empty)


if __name__ == "__main__":
    unittest.main()
