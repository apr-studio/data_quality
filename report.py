import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from file_sys import create_file_path

REPORT_DIR = "reports"
REPORT_FILENAME = "data_quality.json"


def setup_report(run_id: str) -> Path:
    """Create a report path that can be correlated with the pipeline log."""
    report_name = Path(REPORT_FILENAME)
    date = datetime.now().strftime("%Y%m%d")
    filename = f"{report_name.stem}_{date}_{run_id}{report_name.suffix}"
    return create_file_path(dirname=REPORT_DIR, filename=filename)


def generate_quality_report(
    df: pd.DataFrame,
    valid_df: pd.DataFrame,
    issue_df: pd.DataFrame,
    inserted_count: int,
) -> dict:
    """
    計算資料品質統計並產生報告。

    Parameters:
        df: 原始訂單資料。
        valid_df: 有效訂單資料。
        issue_df: 異常問題紀錄。
        inserted_count: 本次新增的異常紀錄數量。

    Returns:
        dict: Data Quality Report。
    """

    if not all(
        isinstance(frame, pd.DataFrame)
        for frame in (df, valid_df, issue_df)
    ):
        raise ValueError("Report inputs must be pandas DataFrames.")

    if (
        not isinstance(inserted_count, int)
        or isinstance(inserted_count, bool)
        or inserted_count < 0
    ):
        raise ValueError("Inserted count must be a non-negative integer.")

    total_records = len(df)
    valid_records = len(valid_df)
    issue_count = len(issue_df)
    if issue_df.empty:
        invalid_records = 0
    else:
        if "order_item_id" not in issue_df.columns:
            raise ValueError("Issue data must include an order_item_id column.")
        if issue_df["order_item_id"].isna().any():
            raise ValueError("Issue order_item_id values cannot be missing.")
        invalid_records = issue_df["order_item_id"].nunique()

    if total_records == 0:
        valid_rate = 0.0
        invalid_rate = 0.0
    else:
        valid_rate = valid_records / total_records * 100
        invalid_rate = invalid_records / total_records * 100

    report = {
        "summary": {
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "issue_count": issue_count,
        },
        "quality_rates": {
            "valid_rate": round(valid_rate, 2),
            "invalid_rate": round(invalid_rate, 2),
        },
        "load_statistics": {
            "inserted_count": inserted_count,
        },
    }

    return report


def save_quality_report(
    report: dict,
    output_path: Path,
) -> None:
    """
    將 Data Quality Report 儲存為 JSON。

    Parameters:
        report: 資料品質報告。
        output_path: JSON 檔案輸出路徑。
    """

    if not isinstance(report, dict):
        raise ValueError("Report must be a dictionary.")
    if not isinstance(output_path, Path):
        raise ValueError("Output path must be a Path object.")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        with output_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )

        logging.info(
            "Data Quality Report 已儲存：%s",
            output_path
        )

    except OSError:
        logging.exception(
            "Data Quality Report 儲存失敗。"
        )
        raise


def create_quality_report(
    df: pd.DataFrame,
    valid_df: pd.DataFrame,
    issue_df: pd.DataFrame,
    inserted_count: int,
    output_path: Path,
) -> dict:
    """
    建立並儲存 Data Quality Report。
    """

    report = generate_quality_report(
        df=df,
        valid_df=valid_df,
        issue_df=issue_df,
        inserted_count=inserted_count,
    )

    save_quality_report(
        report=report,
        output_path=output_path,
    )

    return report