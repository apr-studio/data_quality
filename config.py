import os
from pathlib import Path

from dotenv import load_dotenv


# 無論從哪個工作目錄執行，都讀取專案根目錄的環境設定。
# 先載入預設 .env，再載入本機設定 .env.local；
# 已存在於作業系統的環境變數優先，不會被覆蓋。
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(PROJECT_DIR / ".env.local")

# ===== Database Configuration =====
# 讀取環境變數，並保留本機開發的預設值。

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT_VALUE = os.getenv("DB_PORT", "5432")
try:
    DB_PORT = int(DB_PORT_VALUE)
except (TypeError, ValueError):
    DB_PORT = DB_PORT_VALUE
DB_NAME = os.getenv("DB_NAME", "python_db")
DB_USER = os.getenv("DB_USER", "python_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")