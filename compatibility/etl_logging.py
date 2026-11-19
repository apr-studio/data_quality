import logging

from .file_sys import create_file_path
from .utils.console_handler import create_console_handler
from .utils.file_handler import create_file_handler

LOGGING_END = "========================================================================================================"
LOGGING_DIR = "logs"
LOGGING_FILENAME = "pipeline.log"


def setup_logging(
    run_id: str,
    *,
    omit_repeated_times: bool = True,
    run_id_mode: str = "once",
) -> None:
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
