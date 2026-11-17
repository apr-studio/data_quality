# 設定 logging

import logging
from pathlib import Path


def setup_logging():

    log_dir = Path(__file__).resolve().parent / "logs"

    log_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file = log_dir / "pipeline.log"

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
