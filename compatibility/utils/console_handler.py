import logging

from rich.console import ConsoleRenderable
from rich.logging import RichHandler
from rich.traceback import Traceback

from logging_setup.common import PipelineFormatter, RunIdFilter


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


def create_console_handler(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
    run_id_mode: str = "once",
) -> PipelineRichHandler:
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
