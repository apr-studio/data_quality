import unittest
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_report_contains_overall_and_stage_processing_times(self):
        source = pd.DataFrame({"order_item_id": [1]})
        valid = source.copy()
        issues = pd.DataFrame()
        expected_report = {"summary": {}}

        with ExitStack() as stack:
            stack.enter_context(patch("pipeline.extract_orders", return_value=source))
            stack.enter_context(
                patch("pipeline.transform_orders", return_value=(valid, issues))
            )
            stack.enter_context(patch("pipeline.load_issues", return_value=0))
            stack.enter_context(patch("pipeline.setup_report"))
            create_report = stack.enter_context(
                patch(
                    "pipeline.create_quality_report",
                    return_value=expected_report,
                )
            )
            result = run_pipeline(conn=None, run_id="run-1")

        processing_time = create_report.call_args.kwargs["processing_time"]
        self.assertEqual(result, expected_report)
        started_at = datetime.fromisoformat(processing_time["started_at"])
        finished_at = datetime.fromisoformat(processing_time["finished_at"])
        self.assertIsNotNone(started_at.tzinfo)
        self.assertIsNotNone(finished_at.tzinfo)
        self.assertGreaterEqual(processing_time["duration_seconds"], 0)
        self.assertEqual(
            set(processing_time["stages"]),
            {"extract_seconds", "transform_seconds", "load_seconds"},
        )
        self.assertTrue(
            all(duration >= 0 for duration in processing_time["stages"].values())
        )


if __name__ == "__main__":
    unittest.main()
