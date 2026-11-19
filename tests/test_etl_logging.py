import logging
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from rich.text import Text
from rich.logging import RichHandler

from logging_setup.setup import setup_logging, LOGGING_END
from logging_setup.console_handler import create_console_handler


class SetupLoggingTests(unittest.TestCase):
    def test_log_formatter_includes_run_id_without_trailing_separator(self):
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "pipeline.log"

            with patch(
                "logging_setup.setup.create_file_path",
                return_value=log_path,
            ):
                with patch("logging_setup.setup.logging.basicConfig") as basic_config:
                    setup_logging("run-123", run_id_mode="every")

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
                with patch("logging_setup.console_handler.PipelineRichHandler") as rich_handler:
                    create_console_handler(
                        "run-123",
                        omit_repeated_times=omit_repeated_times,
                        run_id_mode="every",
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
                "logging_setup.setup.create_file_path",
                return_value=log_path,
            ):
                with patch("logging_setup.setup.logging.basicConfig") as basic_config:
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

    def test_console_style_only_affects_console_message(self):
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "pipeline.log"
            with patch(
                "logging_setup.setup.create_file_path",
                return_value=log_path,
            ):
                with patch("logging_setup.setup.logging.basicConfig") as basic_config:
                    setup_logging("run-123")

            file_handler, console_handler = basic_config.call_args.kwargs["handlers"]
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname=__file__,
                lineno=1,
                msg="Pipeline started",
                args=(),
                exc_info=None,
            )
            record.console_style = "bold green"

            try:
                file_handler.filter(record)
                console_handler.filter(record)
                file_message = file_handler.format(record)
                self.assertIn("Pipeline started", file_message)
                self.assertNotIn("bold green", file_message)

                message = Text("Pipeline started")
                with patch.object(
                    RichHandler,
                    "render",
                    return_value=Text("rendered"),
                ) as rich_render:
                    console_handler.render(
                        record=record,
                        traceback=None,
                        message_renderable=message,
                    )

                styled_message = rich_render.call_args.kwargs["message_renderable"]
                self.assertEqual(
                    styled_message.spans[0].style,
                    "bold green",
                )
                self.assertEqual(message.spans, [])
            finally:
                file_handler.close()
                console_handler.close()

    def test_console_renderable_can_use_multiple_colors_without_changing_file_message(self):
        with TemporaryDirectory() as directory:
            log_path = Path(directory) / "pipeline.log"
            with patch(
                "logging_setup.setup.create_file_path",
                return_value=log_path,
            ):
                with patch("logging_setup.setup.logging.basicConfig") as basic_config:
                    setup_logging("run-123")

            file_handler, console_handler = basic_config.call_args.kwargs["handlers"]
            message = "Pipeline 完成！新增異常紀錄：3 筆"
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname=__file__,
                lineno=1,
                msg=message,
                args=(),
                exc_info=None,
            )
            record.console_renderable = Text.assemble(
                ("Pipeline 完成！", "green"),
                ("新增異常紀錄：", "white"),
                ("3 筆", "bold yellow"),
            )

            try:
                file_handler.filter(record)
                console_handler.filter(record)
                self.assertIn(message, file_handler.format(record))

                with patch.object(
                    RichHandler,
                    "render",
                    return_value=Text("rendered"),
                ) as rich_render:
                    console_handler.render(
                        record=record,
                        traceback=None,
                        message_renderable=Text(message),
                    )

                styled_message = rich_render.call_args.kwargs["message_renderable"]
                self.assertEqual(styled_message.plain, message)
                self.assertEqual(
                    [span.style for span in styled_message.spans],
                    ["green", "white", "bold yellow"],
                )
            finally:
                file_handler.close()
                console_handler.close()


if __name__ == "__main__":
    unittest.main()
