from pathlib import Path

def create_file_path( dirname: str ,filename: str = "default.txt" ) -> Path:
    """
    建立檔案路徑。

    Args:
        dirname (str): 資料夾名稱，預設為 "default"。
        filename (str): 檔案名稱，例如 orders.csv，預設為 "default.txt"。
        
    Returns:
        Path: 檔案的完整路徑。
    """
    return create_dir_path(dirname) / filename

def create_dir_path(dirname: str= "default") -> Path:
    """
    建立資料夾路徑

    Args:
            dirname (str): 資料夾名稱，預設為 "default"。
    Returns:
        Path: 資料夾的完整路徑。
    """
    dir_path = get_current_dir_path() / dirname
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

