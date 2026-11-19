# 寫入日誌檔案的處理器建立功能。

import logging
from pathlib import Path

from .common import PipelineFormatter, RunIdFilter


def create_file_handler(log_file: Path, run_id: str) -> logging.FileHandler:
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.addFilter(RunIdFilter(run_id))
    handler.setFormatter(
        PipelineFormatter(
            "%(asctime)s | %(levelname)s | [run=%(run_id)s] | %(message)s"
        )
    )
    return handler
