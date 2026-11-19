# 舊版載入模組相容層。

import logging

from etl.load import load_issues as _load_issues


def load_issues(conn, issue_df):
    """沿用舊版介面載入異常資料。"""
    if issue_df.empty:
        logging.info("沒有異常資料需要寫入。")
        return 0
    return _load_issues(conn, issue_df)
