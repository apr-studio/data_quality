# 設定 logging

import logging
from file_sys import create_file_path 




def setup_logging():
    """
    設定 logging 基本資料，當系統紀錄訊息時，會在 ./logs/pipeline.log 指定的檔案和控制台中顯示。
    """

    log_file = create_file_path(dirname="logs", filename="pipeline.log")

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
    
    """
    檢查 logging 設定是否正確。
    """
    logger = logging.getLogger()
    logger.info("Logging 設定檢查成功。")
    print("Root Level:", logging.getLogger().level)

    for handler in logging.getLogger().handlers:
        print("Handler:", handler)
        print("Handler Level:", handler.level)
