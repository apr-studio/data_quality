import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from infrastructure.paths import create_dir_path, create_file_path


class OutputPathTests(unittest.TestCase):
    def test_create_dir_path_rejects_symlink_to_outside_project(self):
        with TemporaryDirectory() as directory:
            project_path = Path(directory) / "project"
            outside_path = Path(directory) / "outside"
            project_path.mkdir()
            outside_path.mkdir()
            (project_path / "reports").symlink_to(
                outside_path,
                target_is_directory=True,
            )

            with patch(
                "infrastructure.paths.get_current_dir_path",
                return_value=project_path,
            ):
                with self.assertRaises(ValueError):
                    create_dir_path("reports")

    def test_create_file_path_rejects_symlink_target(self):
        with TemporaryDirectory() as directory:
            project_path = Path(directory) / "project"
            reports_path = project_path / "reports"
            outside_path = Path(directory) / "outside.json"
            reports_path.mkdir(parents=True)
            outside_path.touch()
            (reports_path / "report.json").symlink_to(outside_path)

            with patch(
                "infrastructure.paths.get_current_dir_path",
                return_value=project_path,
            ):
                with self.assertRaises(ValueError):
                    create_file_path("reports", "report.json")

    def test_create_file_path_returns_path_within_project(self):
        with TemporaryDirectory() as directory:
            project_path = Path(directory) / "project"
            project_path.mkdir()

            with patch(
                "infrastructure.paths.get_current_dir_path",
                return_value=project_path,
            ):
                result = create_file_path("reports", "report.json")

            self.assertEqual(result, project_path / "reports" / "report.json")


if __name__ == "__main__":
    unittest.main()
