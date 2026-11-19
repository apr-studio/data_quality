# Pipeline 命列執行入口。

import logging
from uuid import uuid4
from rich.text import Text


from infrastructure.database import get_connection
from config.settings import CONSOLE_RUN_ID_MODE, OMIT_REPEATED_TIMES
from logging_setup.setup import setup_logging, LOGGING_END
from pipeline import run_pipeline


def main():
    """初始化日誌並以資料庫連線執行完整 Pipeline。"""
    run_id = uuid4().hex
    setup_logging(
        run_id,
        omit_repeated_times=OMIT_REPEATED_TIMES,
        run_id_mode=CONSOLE_RUN_ID_MODE,
    )

    if CONSOLE_RUN_ID_MODE == "once":
        logging.info(f"Run ID: {run_id}", extra={"console_renderable": Text.assemble({"Run ID: ", "green",},{f"{run_id}","bold yellow"})})

    try:
        with get_connection() as conn:
            run_pipeline(conn, run_id)
    finally:
        logging.info("Pipeline 結束。")
        logging.info(LOGGING_END, extra={"raw_message": True})


if __name__ == "__main__":
    main()
