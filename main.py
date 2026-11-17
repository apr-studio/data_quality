# 執行整個 Pipeline

from db import get_connection
from extract import extract_orders
from transform import transform_orders
from load import load_issues


def main():

    with get_connection() as conn:

        print("PostgreSQL 連線成功！")

        # 1. Extract
        df = extract_orders(conn)

        print("\n原始資料筆數：", len(df))

        # 2. Transform
        valid_df, issue_df = transform_orders(df)

        print("有效資料筆數：", len(valid_df))
        print("異常資料筆數：", len(issue_df))

        # 3. Load
        inserted_count = load_issues(conn, issue_df)

        print("\n資料載入完成！")
        print("本次新增異常紀錄：", inserted_count)


if __name__ == "__main__":
    main()
