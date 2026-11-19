# 設定 logging

import logging
from file_sys import create_file_path 

LOGGING_DIR = "logs"
LOGGING_FILENAME = "pipeline.log"


def setup_logging():
    """
    設定 logging 基本資料，當系統紀錄訊息時，會在 ./logs/pipeline.log 指定的檔案和控制台中顯示。
    """

    log_file = create_file_path(dirname=LOGGING_DIR, filename=LOGGING_FILENAME)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                log_file,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ],
        force=True
    )
  
