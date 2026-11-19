# ETL Pipeline 的主要編排流程。

import logging
import time

from etl.extract import extract_orders
from etl.load import load_issues
from quality.rules import transform_orders
from reporting.quality_report import create_quality_report, setup_report


def run_pipeline(conn, run_id: str) -> dict:
    """依序執行擷取、轉換、載入及報表產生流程。"""
    start_time = time.perf_counter()
    logging.info("Pipeline 開始執行。")

    try:
        logging.info("資料庫連線成功。")

        df = extract_orders(conn)
        logging.info("原始資料筆數：%s", len(df))

        valid_df, issue_df = transform_orders(df)
        logging.info("有效資料筆數：%s", len(valid_df))
        logging.info("異常資料筆數：%s", len(issue_df))

        inserted_count = load_issues(conn, issue_df)
        logging.info("資料載入完成！")
        logging.info("本次新增異常紀錄：%s", inserted_count)

        report = create_quality_report(
            df=df,
            valid_df=valid_df,
            issue_df=issue_df,
            inserted_count=inserted_count,
            output_path=setup_report(run_id),
        )
        logging.info("Pipeline 執行完成。")
        return report

    except Exception as exc:
        logging.exception("Pipeline 執行失敗：%s", exc)
        raise
    finally:
        elapsed_time = time.perf_counter() - start_time
        logging.info("Pipeline 執行時間：%.2f 秒", elapsed_time)
