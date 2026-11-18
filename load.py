# 將結果寫回 PostgresSQL 資料庫

def load_issues(conn, issue_df):
    """
    將異常資料寫入 PostgreSQL 資料庫的 data_quality_issue_log
    表中。

    參數:       
        conn: psycopg 連線物件，用於與資料庫進行互動。  
        issue_df: 包含異常資料的 pandas DataFrame。 
    """

    if issue_df.empty:
        print("沒有異常資料需要寫入。")
        return 0

    query = """
        INSERT INTO public.data_quality_issue_log (
            order_item_id,
            order_id,
            issue_type,
            issue_description
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (order_item_id, issue_type)
        DO NOTHING;
    """

    records = list(
        issue_df[
            [
                "order_item_id",
                "order_id",
                "issue_type",
                "issue_description"
            ]
        ].itertuples(index=False, name=None)
    )

    with conn.cursor() as cur:

        cur.executemany(query, records)

        inserted_count = cur.rowcount

    return inserted_count
