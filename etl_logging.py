# 設定 logging

import logging
from pathlib import Path

from file_sys import create_file_path
from rich.console import ConsoleRenderable
from rich.logging import RichHandler
from rich.traceback import Traceback

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


class PipelineRichHandler(RichHandler):
    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        if getattr(record, "raw_message", False):
            return message_renderable
        return super().render(
            record=record,
            traceback=traceback,
            message_renderable=message_renderable,
        )


def create_file_handler(log_file: Path, run_id: str) -> logging.FileHandler:
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.addFilter(RunIdFilter(run_id))
    handler.setFormatter(
        PipelineFormatter(
            "%(asctime)s | %(levelname)s | [run=%(run_id)s] | %(message)s"
        )
    )
    return handler


def create_console_handler(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
) -> PipelineRichHandler:
    handler = PipelineRichHandler(
        show_time=True,
        omit_repeated_times=omit_repeated_times,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
    )
    handler.addFilter(RunIdFilter(run_id))
    handler.setFormatter(PipelineFormatter("[run=%(run_id)s] %(message)s"))
    return handler


def setup_logging(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
) -> None:
    """
    設定 logging 基本資料，當系統紀錄訊息時，會在 ./logs/pipeline.log 指定的檔案和控制台中顯示。
    """

    log_file = create_file_path(dirname=LOGGING_DIR, filename=LOGGING_FILENAME)
    file_handler = create_file_handler(log_file, run_id)
    console_handler = create_console_handler(
        run_id,
        omit_repeated_times=omit_repeated_times,
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True,
    )
