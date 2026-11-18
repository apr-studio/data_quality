# Data Quality ETL

這個專案從 PostgreSQL 讀取訂單明細，檢查資料品質，計算有效完成訂單的營收，並將異常紀錄寫回 PostgreSQL。

## Pipeline 流程

1. **Extract**：讀取 `public.orders` 中的訂單資料。
2. **Transform**：將已完成、單價不為空且不小於零、數量大於零的明細視為有效資料，並計算 `revenue`。以下狀況會建立異常紀錄：
   - 商品單價缺失（`Missing Unit Price`）
   - 商品單價小於零（`Invalid Unit Price`）；零單價視為有效
   - 數量缺失、為零或小於零（`Invalid Quantity`）
   - 訂單已取消（`Cancelled Order`）
3. **Load**：將異常寫入 `public.data_quality_issue_log`。相同訂單明細與異常類型不會重複新增。

目前有效資料只在轉換階段產生，不會寫回資料庫。

## 環境需求

- Python
- PostgreSQL

## 安裝

在專案根目錄建立並啟用虛擬環境，再安裝相依套件：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell 啟用虛擬環境的指令為：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 資料庫設定

依照環境修改 `config.py` 中的 `DB_HOST`、`DB_PORT`、`DB_NAME` 與 `DB_USER`。執行 Pipeline 時，程式會互動式提示輸入 PostgreSQL 密碼。

資料庫需預先建立以下資料表及欄位：

- `public.orders`：至少包含 `order_item_id`、`order_id`、`unit_price`、`quantity` 和 `status`。
- `public.data_quality_issue_log`：包含 `order_item_id`、`order_id`、`issue_type` 和 `issue_description`，並在 `(order_item_id, issue_type)` 上設定唯一限制，以支援重複執行時略過已存在的異常。

## 執行

確認資料庫設定與必要資料表已備妥後，在專案根目錄執行完整 ETL：

```bash
python main.py
```

`main.py` 會依序讀取訂單、檢查及轉換資料，再呼叫 `load.py` 中的 `load_issues()`，將異常寫入 `public.data_quality_issue_log`。`load.py` 提供載入函式，並非單獨執行的程式入口；請執行 `main.py` 以完成資料庫讀取與寫入。若沒有異常資料，便不會新增紀錄。每次執行新增的筆數會顯示於終端機；相同的訂單明細和異常類型已存在時，資料庫唯一限制會讓它略過。

執行紀錄會顯示於終端機，並寫入 `logs/pipeline.log`。

## 測試

測試使用 Python 內建的 `unittest`，不需額外安裝測試套件，也不需要連接 PostgreSQL。請先依「安裝」章節安裝專案相依套件（測試會使用 `pandas`），並在專案根目錄執行：

```bash
python -m unittest discover -s tests -v
```

單獨執行轉換或資料提取測試：

```bash
python -m unittest discover -s tests -p "test_transform.py" -v
python -m unittest discover -s tests -p "test_extract.py" -v
```

轉換測試涵蓋有效資料、營收及異常判斷；提取測試以 mock 資料庫游標驗證 SQL、欄位名稱、資料列及空結果，不會連接 PostgreSQL。資料庫載入本身不在這些單元測試範圍內，請透過 `python main.py` 執行完整流程。

## 專案結構

```text
.
├── config.py          # PostgreSQL 連線設定
├── db.py              # 資料庫連線
├── extract.py         # 讀取訂單資料
├── transform.py       # 品質檢查與營收計算
├── load.py            # 寫入異常紀錄
├── etl_logging.py     # Pipeline 日誌設定
├── main.py            # Pipeline 入口
└── tests/
    ├── test_extract.py
    └── test_transform.py
```
