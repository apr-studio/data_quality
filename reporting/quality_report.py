# 資料品質報表的統計、產生與儲存功能。

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict

import pandas as pd

from infrastructure.paths import create_file_path


REPORT_DIR = "reports"
REPORT_FILENAME = "data_quality.json"


class ProcessingStages(TypedDict):
    extract_seconds: float
    transform_seconds: float
    load_seconds: float


class ProcessingTime(TypedDict):
    started_at: str
    finished_at: str
    duration_seconds: float
    stages: ProcessingStages


def setup_report(run_id: str) -> Path:
    """建立包含日期與執行識別碼的報表輸出路徑。"""
    report_name = Path(REPORT_FILENAME)
    date = datetime.now().strftime("%Y%m%d")
    filename = f"{report_name.stem}_{date}_{run_id}{report_name.suffix}"
    return create_file_path(dirname=REPORT_DIR, filename=filename)


def generate_quality_report(
    df: pd.DataFrame,
    valid_df: pd.DataFrame,
    issue_df: pd.DataFrame,
    inserted_count: int,
    processing_time: Optional[ProcessingTime] = None,
) -> dict:
    """依輸入資料計算摘要、品質率及載入統計。"""
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
    # 沒有異常資料時，異常筆數為零。
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

    report: dict = {
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
    if processing_time is not None:
        report["processing_time"] = processing_time
    return report


def save_quality_report(report: dict, output_path: Path) -> None:
    """驗證內容後將品質報表寫成 UTF-8 JSON 檔案。"""
    if not isinstance(report, dict):
        raise ValueError("Report must be a dictionary.")
    if not isinstance(output_path, Path):
        raise ValueError("Output path must be a Path object.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4, ensure_ascii=False)
        logging.info("Data Quality Report 已儲存：%s", output_path)
    except OSError:
        logging.exception("Data Quality Report 儲存失敗。")
        raise


def create_quality_report(
    df: pd.DataFrame,
    valid_df: pd.DataFrame,
    issue_df: pd.DataFrame,
    inserted_count: int,
    output_path: Path,
    processing_time: Optional[ProcessingTime] = None,
) -> dict:
    """產生品質統計並儲存至指定路徑。"""
    report = generate_quality_report(
        df=df,
        valid_df=valid_df,
        issue_df=issue_df,
        inserted_count=inserted_count,
        processing_time=processing_time,
    )
    save_quality_report(report=report, output_path=output_path)
    return report
