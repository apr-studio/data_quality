# 訂單資料品質規則與有效資料轉換邏輯。

import pandas as pd


def transform_orders(df):
    """檢查訂單欄位，分離有效資料與異常資料並計算營收。"""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Orders input must be a pandas DataFrame.")

    required_columns = {
        "order_item_id",
        "order_id",
        "unit_price",
        "quantity",
        "status",
    }
    missing_columns = sorted(required_columns.difference(df.columns))
    if missing_columns:
        raise ValueError(
            "Orders data is missing required columns: "
            + ", ".join(missing_columns)
        )

    issues = []

    # 檢查單價是否缺少或為負數。
    invalid_price = df["unit_price"].isna() | (df["unit_price"] < 0)
    for _, row in df[invalid_price].iterrows():
        is_missing = pd.isna(row["unit_price"])
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Missing Unit Price" if is_missing else "Invalid Unit Price",
            "issue_description": (
                "Unit price is missing"
                if is_missing
                else "Unit price must not be negative"
            ),
        })

    # 檢查數量是否缺少、等於零或為負數。
    invalid_quantity = df["quantity"].isna() | (df["quantity"] <= 0)
    for _, row in df[invalid_quantity].iterrows():
        is_missing = pd.isna(row["quantity"])
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Missing Quantity" if is_missing else "Invalid Quantity",
            "issue_description": (
                "Quantity is missing"
                if is_missing
                else "Quantity must be greater than zero"
            ),
        })

    # 已取消訂單會另外建立異常紀錄。
    cancelled = df["status"] == "Cancelled"
    for _, row in df[cancelled].iterrows():
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Cancelled Order",
            "issue_description": "Order has been cancelled",
        })

    issue_df = pd.DataFrame(issues)
    # 只有完成且欄位有效的訂單才會計入有效資料與營收。
    valid_mask = (
        (df["status"] == "Completed")
        & df["unit_price"].notna()
        & (df["unit_price"] >= 0)
        & df["quantity"].notna()
        & (df["quantity"] > 0)
    )
    valid_df = df.loc[valid_mask].copy()
    valid_df["revenue"] = valid_df["quantity"] * valid_df["unit_price"]

    return valid_df, issue_df
