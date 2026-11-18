# 從 PostgresSQL 資料庫中提取資料

import pandas as pd


def extract_orders(conn):
    """
    從 PostgreSQL 資料庫中提取訂單資料。
    
    參數:
        conn: psycopg 連線物件，用於與資料庫進行互動。  
    """

    query = """
        SELECT *
        FROM public.orders
        ORDER BY order_item_id;
    """

    with conn.cursor() as cur:

        cur.execute(query)

        rows = cur.fetchall()

        columns = [
            description.name
            for description in cur.description
        ]

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    return df