# 建立資料庫連線

import psycopg
from getpass import getpass

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER
)


def get_connection():

    password = getpass("請輸入 PostgreSQL 密碼：")

    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=password
    )

    return conn