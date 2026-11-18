# 分析及處理資料

import pandas as pd


def transform_orders(df):

    # 建立異常紀錄
    issues = []

    # 1. 檢查缺少商品單價
    missing_price = df["unit_price"].isna()

    for _, row in df[missing_price].iterrows():
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Missing Unit Price",
            "issue_description": "Unit price is missing"
        })

    # 2. 檢查無效數量
    invalid_quantity = df["quantity"].isna() | (df["quantity"] <= 0)

    for _, row in df[invalid_quantity].iterrows():
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Invalid Quantity",
            "issue_description": "Quantity must be present and greater than zero"
        })

    # 3. 檢查取消訂單
    cancelled = df["status"] == "Cancelled"

    for _, row in df[cancelled].iterrows():
        issues.append({
            "order_item_id": row["order_item_id"],
            "order_id": row["order_id"],
            "issue_type": "Cancelled Order",
            "issue_description": "Order has been cancelled"
        })

    # 建立異常資料 DataFrame
    issue_df = pd.DataFrame(issues)

    # 篩選有效資料
    valid_mask = (
        (df["status"] == "Completed")
        & df["unit_price"].notna()
        & (df["quantity"] > 0)
    )

    valid_df = df.loc[valid_mask].copy()

    # 計算營收
    valid_df["revenue"] = (
        valid_df["quantity"] * valid_df["unit_price"]
    )

    return valid_df, issue_df