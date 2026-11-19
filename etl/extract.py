# 從 PostgreSQL 擷取訂單資料。

import pandas as pd


def extract_orders(conn) -> pd.DataFrame:
    """執行訂單查詢，並將資料庫欄位名稱轉為 DataFrame 欄位。"""
    query = """
        SELECT *
        FROM public.orders
        ORDER BY order_item_id;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [description.name for description in cur.description]

    return pd.DataFrame(rows, columns=columns)
