# 建立資料庫連線

import psycopg
from getpass import getpass

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER
)


REQUIRED_DB_CONFIG = (
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
)


class DatabaseConfigurationError(ValueError):
    """資料庫設定不完整或無效。"""


class DatabaseConnectionError(RuntimeError):
    """資料庫連線建立失敗。"""


def validate_db_config():
    """
    確認 config.py 所需的資料庫參數都已設定且有效。

    未設定或無效時拋出例外，由呼叫端（main.py）統一處理。
    """

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


def get_connection():
    """
    建立與 PostgreSQL 資料庫的連線。
    """

    try:
        validate_db_config()

        password = getpass("請輸入 PostgreSQL 密碼：")
        if not password or not password.strip():
            raise DatabaseConfigurationError(
                "資料庫設定不完整：未輸入 PostgreSQL 密碼"
            )

        return psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=password,
        )
    except DatabaseConfigurationError:
        raise
    except psycopg.Error as exc:
        raise DatabaseConnectionError(
            f"無法連線 PostgreSQL：{exc}"
        ) from exc