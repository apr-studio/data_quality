import logging
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from rich.text import Text
from rich.logging import RichHandler

from etl_logging import create_console_handler, setup_logging, LOGGING_END


class SetupLoggingTests(unittest.TestCase):
    def test_log_formatter_includes_run_id_without_trailing_separator(self):
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "pipeline.log"

            with patch(
                "etl_logging.create_file_path",
                return_value=log_path,
            ):
                with patch("etl_logging.logging.basicConfig") as basic_config:
                    setup_logging("run-123")

            handlers = basic_config.call_args.kwargs["handlers"]
            self.assertIsInstance(handlers[0], logging.FileHandler)
            self.assertIsInstance(handlers[1], RichHandler)
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname=__file__,
                lineno=1,
                msg="Pipeline started",
                args=(),
                exc_info=None,
            )

            formatted = []
            try:
                for handler in handlers:
                    self.assertTrue(handler.filter(record))
                    formatted.append(handler.format(record))
            finally:
                for handler in handlers:
                    handler.close()

            for message in formatted:
                self.assertIn("[run=run-123]", message)
                self.assertIn("Pipeline started", message)

    def test_can_choose_whether_to_omit_repeated_times(self):
        for omit_repeated_times in (True, False):
            with self.subTest(omit_repeated_times=omit_repeated_times):
                with patch("etl_logging.PipelineRichHandler") as rich_handler:
                    create_console_handler(
                        "run-123",
                        omit_repeated_times=omit_repeated_times,
                    )

                rich_handler.assert_called_once_with(
                    show_time=True,
                    omit_repeated_times=omit_repeated_times,
                    show_level=True,
                    show_path=False,
                    rich_tracebacks=True,
                )

    def test_raw_message_formatter_omits_default_fields(self):
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "pipeline.log"

            with patch(
                "etl_logging.create_file_path",
                return_value=log_path,
            ):
                with patch("etl_logging.logging.basicConfig") as basic_config:
                    setup_logging("run-123")

            handlers = basic_config.call_args.kwargs["handlers"]
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname=__file__,
                lineno=1,
                msg=LOGGING_END,
                args=(),
                exc_info=None,
            )
            record.raw_message = True

            try:
                for handler in handlers:
                    self.assertTrue(handler.filter(record))
                    self.assertEqual(handler.format(record), LOGGING_END)
                console_handler = handlers[1]
                message = Text(LOGGING_END)
                rendered = console_handler.render(
                    record=record,
                    traceback=None,
                    message_renderable=message,
                )
                self.assertIs(rendered, message)
            finally:
                for handler in handlers:
                    handler.close()


if __name__ == "__main__":
    unittest.main()
