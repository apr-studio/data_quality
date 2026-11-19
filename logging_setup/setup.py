# 日誌系統初始化與處理器組合。

import logging

from infrastructure.paths import create_file_path
from .console_handler import create_console_handler
from .file_handler import create_file_handler


LOGGING_DIR = "logs"
LOGGING_FILENAME = "pipeline.log"
LOGGING_END = "========================================================================================================"


def setup_logging(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
    run_id_mode: str = "once",
) -> None:
    """設定檔案及終端機日誌處理器，並套用到全域 logger。"""
    log_file = create_file_path(dirname=LOGGING_DIR, filename=LOGGING_FILENAME)
    file_handler = create_file_handler(log_file, run_id)
    console_handler = create_console_handler(
        run_id,
        omit_repeated_times=omit_repeated_times,
        run_id_mode=run_id_mode,
    )
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True,
    )
