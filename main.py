# 執行整個 Pipeline

from db import get_connection
from extract import extract_orders


def main():

    with get_connection() as conn:

        print("PostgreSQL 連線成功！")

        df = extract_orders(conn)

        print("\n資料擷取成功！")

        print("資料形狀：", df.shape)

        print("\n資料預覽：")

        print(df.head())


if __name__ == "__main__":
    main()