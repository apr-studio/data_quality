from pathlib import Path

from infrastructure.paths import create_file_path
from reporting.quality_report import (
    REPORT_DIR,
    REPORT_FILENAME,
    generate_quality_report,
    save_quality_report,
)


def setup_report(run_id: str) -> Path:
    report_name = Path(REPORT_FILENAME)
    from datetime import datetime

    date = datetime.now().strftime("%Y%m%d")
    filename = f"{report_name.stem}_{date}_{run_id}{report_name.suffix}"
    return create_file_path(dirname=REPORT_DIR, filename=filename)


def create_quality_report(
    df,
    valid_df,
    issue_df,
    inserted_count: int,
    output_path: Path,
) -> dict:
    report = generate_quality_report(
        df=df,
        valid_df=valid_df,
        issue_df=issue_df,
        inserted_count=inserted_count,
    )
    save_quality_report(report=report, output_path=output_path)
    return report