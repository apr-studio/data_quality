# 日誌共用格式器與執行識別碼過濾器。

import logging


class RunIdFilter(logging.Filter):
    """將目前 Pipeline 執行識別碼加入每一筆日誌紀錄。"""
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = self.run_id
        return True


class PipelineFormatter(logging.Formatter):
    """支援直接輸出原始分隔線，不套用一般日誌欄位格式。"""
    def format(self, record: logging.LogRecord) -> str:
        if getattr(record, "raw_message", False):
            return record.getMessage()
        return super().format(record)
