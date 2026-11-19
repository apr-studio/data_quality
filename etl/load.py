# 將資料品質異常結果載入 PostgreSQL。

import logging


def load_issues(conn, issue_df) -> int:
    """批次寫入異常紀錄，並回傳實際新增筆數。"""
    if issue_df.empty:
        logging.info("沒有異常資料需要寫入。")
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
            ["order_item_id", "order_id", "issue_type", "issue_description"]
        ].itertuples(index=False, name=None)
    )

    with conn.cursor() as cur:
        cur.executemany(query, records)
        inserted_count = cur.rowcount

    return inserted_count
