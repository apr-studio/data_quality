import json
import logging

from pathlib import Path
from file_sys import create_file_path

REPORT_DIR = "reports"
REPORT_FILENAME = "data_quality.json"


def setup_report() -> Path:
    """
    設定報告檔案的路徑，並確保目錄存在。

    Returns:
        Path: 報告檔案的路徑。
    """
    report_path = create_file_path(dirname=REPORT_DIR, filename=REPORT_FILENAME)  
    
    return report_path


def generate_quality_report(
    total_records: int,
    valid_records: int,
    invalid_records: int,
) -> dict:
    """
    生成資料品質報告，包含總筆數、有效筆數、異常筆數以及有效率和異常率。
    Args:
        total_records (int): 總筆數。
        valid_records (int): 有效筆數。
        invalid_records (int): 異常筆數。       

    Returns:
        dict: 資料品質報告，包含總筆數、有效筆數、
    """

    record_counts = (total_records, valid_records, invalid_records)
    if any(
        not isinstance(count, int) or isinstance(count, bool)
        for count in record_counts
    ):
        raise ValueError("Record counts must be integers.")

    if total_records < 0:
        raise ValueError("Total records cannot be negative.")

    if valid_records < 0 or invalid_records < 0:
        raise ValueError("Record counts cannot be negative.")

    if valid_records + invalid_records != total_records:
        raise ValueError("Record counts do not match.")

    if total_records == 0:
        valid_rate = 0.0
        invalid_rate = 0.0
    else:
        valid_rate = valid_records / total_records * 100
        invalid_rate = invalid_records / total_records * 100

    report = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "valid_rate": round(valid_rate, 2),
        "invalid_rate": round(invalid_rate, 2),
    }

    return report


def save_quality_report(
    report: dict,
    output_path: Path,
) -> None:
    """
    將資料品質報告保存為 JSON 檔案。
    
    Args:
        report (dict): 資料品質報告。
        output_path (Path): 報告檔案的路徑。
    
    Raises:
        ValueError: 如果 report 不是字典或 output_path 不是 Path 物件。
    """

    if not isinstance(report, dict):
        raise ValueError("Report must be a dictionary.")

    if not isinstance(output_path, Path):
        raise ValueError("Output path must be a Path object.")  
    
    # 確保輸出路徑的父目錄存在
    if not output_path.parent.exists():
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
   

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

    logging.info("Data Quality Report saved: %s", output_path)