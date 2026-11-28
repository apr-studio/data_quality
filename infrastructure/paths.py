# 專案輸出檔案與目錄的共用路徑工具。

from pathlib import Path
import logging
import re


DEFAULT_DIRNAME = "default"
DEFAULT_FILENAME = "default.txt"
DEFAULT_DIR_PATTERN = r"[\w-]+"
DEFAULT_FILE_PATTERN = r"[\w.-]+"


def get_correct_name(
    name: str | None,
    defaultname: str,
    pattern: str,
    err_message: str,
) -> str:
    """驗證名稱格式；無效名稱會回傳預設名稱並記錄警告。"""
    if name is None or (isinstance(name, str) and not name.strip()):
        return defaultname

    if not isinstance(name, str):
        logging.warning(err_message)
        return defaultname

    name = name.strip()
    if name in {".", ".."} or not re.fullmatch(pattern, name):
        logging.warning(err_message)
        return defaultname

    return name


def get_dirname(dirname: str = DEFAULT_DIRNAME) -> str:
    """取得經過驗證的資料夾名稱。"""
    return get_correct_name(
        name=dirname,
        defaultname=DEFAULT_DIRNAME,
        pattern=DEFAULT_DIR_PATTERN,
        err_message=f"資料夾名稱 '{dirname}' 不合法，將使用預設值 '{DEFAULT_DIRNAME}'。",
    )


def get_filename(filename: str = DEFAULT_FILENAME) -> str:
    """取得經過驗證的檔案名稱。"""
    return get_correct_name(
        name=filename,
        defaultname=DEFAULT_FILENAME,
        pattern=DEFAULT_FILE_PATTERN,
        err_message=f"檔案名稱 '{filename}' 不合法，將使用預設值 '{DEFAULT_FILENAME}'。",
    )


def create_dir_path(dirname: str = DEFAULT_DIRNAME) -> Path:
    """建立專案根目錄下的指定資料夾並回傳路徑。"""
    project_path = get_current_dir_path()
    dir_path = project_path / get_dirname(dirname)
    _validate_project_path(dir_path, project_path)
    if dir_path.is_symlink():
        raise ValueError("輸出目錄不得為符號連結。")

    dir_path.mkdir(parents=True, exist_ok=True)
    _validate_project_path(dir_path, project_path)
    if dir_path.is_symlink():
        raise ValueError("輸出目錄不得為符號連結。")

    return dir_path


def create_file_path(
    dirname: str = DEFAULT_DIRNAME,
    filename: str = DEFAULT_FILENAME,
) -> Path:
    """建立完整檔案路徑；必要時會自動建立父資料夾。"""
    dir_path = create_dir_path(dirname)
    file_path = dir_path / get_filename(filename)
    _validate_project_path(file_path, get_current_dir_path())
    if file_path.is_symlink():
        raise ValueError("輸出檔案不得為符號連結。")
    return file_path


def get_current_dir_path() -> Path:
    """取得專案根目錄，而不受執行時工作目錄影響。"""
    return Path(__file__).resolve().parents[1]


def _validate_project_path(path: Path, project_path: Path) -> None:
    """拒絕解析後位於專案根目錄之外的輸出路徑。"""
    try:
        path.resolve().relative_to(project_path.resolve())
    except ValueError as exc:
        raise ValueError("輸出路徑不得超出專案根目錄。") from exc
