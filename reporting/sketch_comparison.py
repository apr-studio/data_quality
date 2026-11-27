import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


def _report_run_at(report: dict, path: Path) -> Optional[datetime]:
    for field in ("processing_time", "report_time"):
        timing = report.get(field)
        if timing is None:
            continue
        if not isinstance(timing, dict):
            raise ValueError(f"{field} must be an object: {path}")

        started_at = timing.get("started_at")
        if started_at is None:
            continue
        if not isinstance(started_at, str):
            raise ValueError(f"{field}.started_at must be a string: {path}")
        try:
            run_at = datetime.fromisoformat(started_at)
        except ValueError as exc:
            raise ValueError(
                f"{field}.started_at is not a valid ISO timestamp: {path}"
            ) from exc
        if run_at.utcoffset() is None:
            raise ValueError(f"{field}.started_at must include a timezone: {path}")
        return run_at

    return None


def compare_reports(report_directory: Path = Path("reports")) -> pd.DataFrame:
    rows = []
    for path in report_directory.glob("data_quality_*.json"):
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict):
            raise ValueError(f"Report must contain a JSON object: {path}")

        run_at = _report_run_at(report, path)
        if run_at is None:
            print(f"略過缺少執行時間的報表：{path.name}")
            continue

        summary = report["summary"]
        rates = report["quality_rates"]
        rows.append({
            "file": path.name,
            "run_at": run_at,
            "total": summary["total_records"],
            "valid": summary["valid_records"],
            "invalid": summary["invalid_records"],
            "issues": summary["issue_count"],
            "valid_rate": rates["valid_rate"],
            "invalid_rate": rates["invalid_rate"],
            "inserted": report["load_statistics"]["inserted_count"],
        })

    if len(rows) < 2:
        raise ValueError("至少需要兩份含有效執行時間的報表。")

    comparison = pd.DataFrame(rows).sort_values("run_at").reset_index(drop=True)
    comparison["invalid_change"] = comparison["invalid"].diff()
    comparison["valid_rate_change"] = comparison["valid_rate"].diff()
    return comparison


if __name__ == "__main__":
    print(compare_reports().to_string(index=False))
