# 舊版資料庫模組相容層；實際連線邏輯仍集中於 infrastructure。

import psycopg

from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


REQUIRED_DB_CONFIG = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
)


class DatabaseConfigurationError(ValueError):
    """資料庫設定不完整或無效。"""


class DatabaseConnectionError(RuntimeError):
    """資料庫連線建立失敗。"""


def validate_db_config() -> None:
    """沿用舊模組介面，並使用相同規則驗證資料庫設定。"""
    missing_names = []
    values = globals()

    for name in REQUIRED_DB_CONFIG:
        value = values.get(name)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_names.append(name)

    if missing_names:
        raise DatabaseConfigurationError(
            "資料庫設定不完整，請設定：" + "、".join(missing_names)
        )

    if isinstance(DB_PORT, bool) or not isinstance(DB_PORT, int):
        raise DatabaseConfigurationError("資料庫設定無效：DB_PORT 必須是整數")
    if not 1 <= DB_PORT <= 65535:
        raise DatabaseConfigurationError(
            "資料庫設定無效：DB_PORT 必須介於 1 到 65535"
        )


def get_connection():
    """沿用舊版 get_connection 名稱建立 PostgreSQL 連線。"""
    try:
        validate_db_config()
        return psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
    except DatabaseConfigurationError:
        raise
    except psycopg.Error as exc:
        raise DatabaseConnectionError(
            f"無法連線 PostgreSQL：{exc}"
        ) from exc
