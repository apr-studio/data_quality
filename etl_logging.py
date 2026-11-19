# 設定 logging

import logging

from file_sys import create_file_path

LOGGING_DIR = "logs"
LOGGING_FILENAME = "pipeline.log"

LOGGING_END = "========================================================================================================"


class RunIdFilter(logging.Filter):
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = self.run_id
        return True


class PipelineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if getattr(record, "raw_message", False):
            return record.getMessage()
        return super().format(record)


def setup_logging(run_id: str) -> None:
    """
    設定 logging 基本資料，當系統紀錄訊息時，會在 ./logs/pipeline.log 指定的檔案和控制台中顯示。
    """

    log_file = create_file_path(dirname=LOGGING_DIR, filename=LOGGING_FILENAME)
    run_id_filter = RunIdFilter(run_id)
    formatter = PipelineFormatter(
        "%(asctime)s | %(levelname)s | [run=%(run_id)s] | %(message)s"
    )
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    console_handler = logging.StreamHandler()
    for handler in (file_handler, console_handler):
        handler.addFilter(run_id_filter)
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True,
    )
