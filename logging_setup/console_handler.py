# 統一終端機日誌輸出格式的 Rich handler。

import logging

from rich.console import ConsoleRenderable
from rich.logging import RichHandler
from rich.text import Text
from rich.traceback import Traceback

from .common import PipelineFormatter, RunIdFilter


class PipelineRichHandler(RichHandler):
    """保留分隔線的原始文字，不額外加上 Rich 日誌欄位。"""
    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        if getattr(record, "raw_message", False):
            return message_renderable
        console_renderable = getattr(record, "console_renderable", None)
        if console_renderable is not None:
            if not isinstance(console_renderable, Text):
                raise TypeError("console_renderable 必須是 rich.text.Text")
            message_renderable = console_renderable
        console_style = getattr(record, "console_style", None)
        if console_style and isinstance(message_renderable, Text):
            message_renderable = message_renderable.copy()
            message_renderable.stylize(console_style)
        return super().render(
            record=record,
            traceback=traceback,
            message_renderable=message_renderable,
        )


def create_console_handler(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
    run_id_mode: str = "once",
) -> PipelineRichHandler:
    """建立終端機處理器並設定執行識別碼顯示模式。"""
    if run_id_mode not in ("once", "every"):
        raise ValueError("run_id_mode 必須是 'once' 或 'every'")

    handler = PipelineRichHandler(
        show_time=True,
        omit_repeated_times=omit_repeated_times,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
    )
    handler.addFilter(RunIdFilter(run_id))
    console_format = (
        "[run=%(run_id)s] %(message)s"
        if run_id_mode == "every"
        else "%(message)s"
    )
    handler.setFormatter(PipelineFormatter(console_format))
    return handler
