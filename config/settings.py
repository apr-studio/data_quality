# 從環境變數及本機設定檔載入專案設定。

import os
from pathlib import Path

from dotenv import dotenv_values


PROJECT_DIR = Path(__file__).resolve().parents[1]

file_settings = {}
file_settings.update(dotenv_values(PROJECT_DIR / ".env"))
file_settings.update(dotenv_values(PROJECT_DIR / ".env.local"))

# System environment variables have the highest priority.
for name, value in file_settings.items():
    if value is not None:
        os.environ.setdefault(name, value)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT_VALUE = os.getenv("DB_PORT", "5432")
try:
    DB_PORT = int(DB_PORT_VALUE)
except (TypeError, ValueError):
    DB_PORT = DB_PORT_VALUE
DB_NAME = os.getenv("DB_NAME", "python_db")
DB_USER = os.getenv("DB_USER", "python_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CONNECT_TIMEOUT_VALUE = os.getenv("DB_CONNECT_TIMEOUT", "10")
try:
    DB_CONNECT_TIMEOUT = int(DB_CONNECT_TIMEOUT_VALUE)
except (TypeError, ValueError):
    DB_CONNECT_TIMEOUT = DB_CONNECT_TIMEOUT_VALUE

CONSOLE_RUN_ID_MODE = os.getenv("CONSOLE_RUN_ID_MODE", "once").strip().lower()
if CONSOLE_RUN_ID_MODE not in ("once", "every"):
    raise ValueError("CONSOLE_RUN_ID_MODE 必須是 once 或 every")

OMIT_REPEATED_TIMES_VALUE = os.getenv(
    "OMIT_REPEATED_TIMES",
    "true",
).strip().lower()

if OMIT_REPEATED_TIMES_VALUE not in ("true", "false"):
    raise ValueError("OMIT_REPEATED_TIMES 必須是 true 或 false")

OMIT_REPEATED_TIMES = OMIT_REPEATED_TIMES_VALUE == "true"
