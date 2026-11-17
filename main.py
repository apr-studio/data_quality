# 執行整個 Pipeline

from db import get_connection
from extract import extract_orders
from transform import transform_orders


def main():

    with get_connection() as conn:

        print("PostgreSQL 連線成功！")

        # Extract
        df = extract_orders(conn)

        print("\n原始資料筆數：", len(df))

        # Transform
        valid_df, issue_df = transform_orders(df)

        print("\n資料轉換完成！")

        print("有效資料筆數：", len(valid_df))
        print("異常資料筆數：", len(issue_df))

        print("\n異常類型統計：")
        print(issue_df["issue_type"].value_counts())

        print("\n有效資料營收：")
        print(valid_df["revenue"].sum())


if __name__ == "__main__":
    main()