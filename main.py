# 執行整個 Pipeline

from db import get_connection
from extract import extract_orders
from transform import transform_orders
from load import load_issues
from etl_logging import setup_logging, LOGGING_END
import logging
import time
from uuid import uuid4
from report import create_quality_report, setup_report


def main():
    """
    執行整個 ETL Pipeline，包括 Extract、Transform 和 Load 三個步驟。
    """

    run_id = uuid4().hex
    setup_logging(run_id)

    start_time = time.perf_counter()

    logging.info("Pipeline 開始執行。")

    try :
        with get_connection() as conn:

            logging.info("資料庫連線成功。")

            # 1. Extract
            df = extract_orders(conn)

            logging.info(f"原始資料筆數：{len(df)}")


            # 2. Transform
            valid_df, issue_df = transform_orders(df)

            logging.info(f"有效資料筆數：{len(valid_df)}")
            logging.info(f"異常資料筆數：{len(issue_df)}")

            # 3. Load
            inserted_count = load_issues(conn, issue_df)

            logging.info(f"資料載入完成！")
            logging.info(f"本次新增異常紀錄：{inserted_count}")

            # 4. Generate and Save Report
            create_quality_report(
                df=df,
                valid_df=valid_df,
                issue_df=issue_df,
                inserted_count=inserted_count,
                output_path=setup_report(run_id),
            )

        logging.info("Pipeline 執行完成。")

    except Exception as e:
        logging.exception(f"Pipeline 執行失敗：{e}")
        raise 
    finally:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"Pipeline 執行時間：{elapsed_time:.2f} 秒")
        logging.info("Pipeline 結束。")
        logging.info(LOGGING_END, extra={"raw_message": True})


if __name__ == "__main__":
    main()
