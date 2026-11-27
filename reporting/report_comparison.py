"""Compare summary metrics across generated quality reports."""

import json
import logging
from collections.abc import Iterable
from datetime import datetime
from numbers import Real
from pathlib import Path
from typing import Optional

import pandas as pd


_METRIC_FIELDS = {
    "total_records": ("summary", "total_records"),
    "valid_records": ("summary", "valid_records"),
    "invalid_records": ("summary", "invalid_records"),
    "issue_count": ("summary", "issue_count"),
    "valid_rate": ("quality_rates", "valid_rate"),
    "invalid_rate": ("quality_rates", "invalid_rate"),
    "inserted_count": ("load_statistics", "inserted_count"),
}


def _get_report_timestamp(report: dict, path: Path) -> Optional[datetime]:
    for field in ("processing_time", "report_time"):
        timing = report.get(field)
        if timing is None:
            continue
        if not isinstance(timing, dict):
            raise ValueError(f"Report {field} must be an object: {path}")

        started_at = timing.get("started_at")
        if started_at is None:
            continue
        if not isinstance(started_at, str):
            raise ValueError(
                f"Report {field}.started_at must be a string: {path}"
            )
        try:
            run_at = datetime.fromisoformat(started_at)
        except ValueError as exc:
            message = (
                f"Report {field}.started_at is not a valid "
                f"ISO timestamp: {path}"
            )
            raise ValueError(message) from exc
        if run_at.utcoffset() is None:
            raise ValueError(
                f"Report {field}.started_at must include a timezone: {path}"
            )
        return run_at

    logging.warning(
        "Skipping report without processing_time.started_at or "
        "report_time.started_at: %s",
        path,
    )
    return None


def compare_quality_reports(report_paths: Iterable[Path]) -> pd.DataFrame:
    """Return report metrics in run order with changes from the previous run."""
    paths = list(report_paths)
    if len(paths) < 2:
        raise ValueError("At least two report paths are required.")

    rows = []
    for path in paths:
        with path.open(encoding="utf-8") as file:
            report = json.load(file)
        if not isinstance(report, dict):
            raise ValueError(f"Report must contain a JSON object: {path}")

        try:
            metrics = {
                name: report[section][field]
                for name, (section, field) in _METRIC_FIELDS.items()
            }
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Report is missing required fields: {path}") from exc

        run_at = _get_report_timestamp(report, path)
        if run_at is None:
            continue

        for name, value in metrics.items():
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError(f"Report metric {name} must be numeric: {path}")

        rows.append({
            "report_file": path.name,
            "run_at": run_at,
            **metrics,
        })

    if len(rows) < 2:
        raise ValueError("At least two reports with timestamps are required.")

    comparison = pd.DataFrame(rows).sort_values("run_at").reset_index(drop=True)
    for metric in _METRIC_FIELDS:
        comparison[f"{metric}_change"] = comparison[metric].diff()
    return comparison


# comparison = compare_quality_reports(Path("reports").glob("data_quality_*.json"))
# print(comparison.to_string(index=False))