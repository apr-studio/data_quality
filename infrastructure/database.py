# 資料庫連線與設定驗證模組。

import psycopg

from config.settings import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_CONNECT_TIMEOUT,
)


REQUIRED_DB_CONFIG = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_CONNECT_TIMEOUT",
)


class DatabaseConfigurationError(ValueError):
    """資料庫設定不完整或無效。"""


class DatabaseConnectionError(RuntimeError):
    """資料庫連線建立失敗。"""


def validate_db_config() -> None:
    """確認所有必要資料庫設定均存在且格式有效。"""
    missing_names = []

    for name in REQUIRED_DB_CONFIG:
        value = globals().get(name)
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

    if (
        isinstance(DB_CONNECT_TIMEOUT, bool)
        or not isinstance(DB_CONNECT_TIMEOUT, int)
    ):
        raise DatabaseConfigurationError(
            "資料庫設定無效：DB_CONNECT_TIMEOUT 必須是整數"
        )

    if not 1 <= DB_CONNECT_TIMEOUT <= 300:
        raise DatabaseConfigurationError(
            "資料庫設定無效：DB_CONNECT_TIMEOUT 必須介於 1 到 300"
        )


def get_connection():
    """建立 PostgreSQL 連線；設定或連線失敗時拋出具名例外。"""
    try:
        validate_db_config()
        return psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            connect_timeout=DB_CONNECT_TIMEOUT,
            password=DB_PASSWORD,
        )
    except DatabaseConfigurationError:
        raise
    except psycopg.Error as exc:
        raise DatabaseConnectionError(
            f"無法連線 PostgreSQL：{exc}"
        ) from exc
