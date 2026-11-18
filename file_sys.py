from pathlib import Path
import re
import logging

DEFAULT_DIRNAME = "default"
DEFAULT_FILENAME = "default.txt"
DEFAULT_DIR_PATTERN = r'[\w-]+'
DEFAULT_FILE_PATTERN = r'[\w.-]+'



def get_correct_name(
    name: str | None,
    defaultname: str,
    pattern: str,
    err_message: str,
) -> str:
    """
    取得正確的名稱，如果 name 為 None、空字串或不合法的字元，則回傳預設值 defaultname。

    Args:
        name (str): 名稱。
        defaultname (str): 預設名稱。
        pattern (str): 正則表達式，用於驗證名稱的合法性。
        err_message (str): 在 Terminal 顯示錯誤訊息。

    Returns:
        str: 正確的名稱。
    """
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
    """
    取得資料夾名稱。

    Args:
        dirname (str): 資料夾名稱，預設為 "default"。

    Returns:
        str: 資料夾名稱，如果 dirname 為 None、空字串或不合法的字元，則回傳預設值 DEFAULT_DIRNAME。
    """
    
    return get_correct_name(name= dirname, defaultname=DEFAULT_DIRNAME,pattern=DEFAULT_DIR_PATTERN, err_message= f"資料夾名稱 '{dirname}' 不合法，將使用預設值 '{DEFAULT_DIRNAME}'。")

def get_filename(filename: str = DEFAULT_FILENAME) -> str:
    """
    取得檔案名稱。

    Args:
        filename (str): 檔案名稱，預設為 "default.txt"。


    Returns:
        str: 檔案名稱，如果 filename 為 None、空字串或不合法的字元，則回傳預設值 DEFAULT_FILENAME。
    """


    return get_correct_name(name=filename, defaultname=DEFAULT_FILENAME,pattern=DEFAULT_FILE_PATTERN, err_message=f"檔案名稱 '{filename}' 不合法，將使用預設值 '{DEFAULT_FILENAME}'。")

 

def create_file_path( dirname: str = DEFAULT_DIRNAME,filename: str = DEFAULT_FILENAME ) -> Path:
    """
    建立檔案路徑。

    Args:
        dirname (str): 資料夾名稱，預設為 "default"。
        filename (str): 檔案名稱，例如 orders.csv，預設為 "default.txt"。
        
    Returns:
        Path: 檔案的完整路徑。
    """
    return create_dir_path(dirname) / get_filename(filename)

def create_dir_path(dirname: str= DEFAULT_DIRNAME) -> Path:
    """
    建立資料夾路徑

    Args:
            dirname (str): 資料夾名稱，預設為 "default"。
    Returns:
        Path: 資料夾的完整路徑。
    """
    dir_path = get_current_dir_path() / get_dirname(dirname)
    dir_path.mkdir(
        parents=True,
        exist_ok=True
    )
    return dir_path 

def get_current_dir_path() -> Path:
    """
    取得資料夾路徑

    Returns:
        Path: 當前資料夾的完整路徑。
    """
    return Path(__file__).resolve().parent

