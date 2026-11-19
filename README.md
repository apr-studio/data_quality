# Data Quality ETL

這個專案會從 PostgreSQL 擷取訂單明細、檢查資料品質、計算營收與異常紀錄，並將結果寫回資料庫及產生品質報表。

## Pipeline 流程

1. **Extract**：讀取 `public.orders` 的訂單資料。
2. **Transform**：
   - 已完成、單價不為空且不小於零、數量大於零的明細視為有效資料。
   - 計算有效資料的營收。
   - 以下資料會建立異常紀錄：商品單價缺失、單價小於零、數量缺失或無效、訂單已取消。
3. **Load**：將異常寫入 `public.data_quality_issue_log`；唯一限制會避免重複新增。
4. **Report**：產生每次執行獨立的 JSON 品質報表。

有效資料只會在轉換階段產生，不會寫回資料庫。

## 環境需求

- Python 3
- PostgreSQL
- 專案相依套件：見 `requirements.txt`

## 安裝

在專案根目錄建立並啟用虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 環境設定

複製 `.env.example`：

```bash
cp .env.example .env.local
```

然後修改 `.env.local`：

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=python_db
DB_USER=elena
DB_PASSWORD=你的資料庫密碼

CONSOLE_RUN_ID_MODE=once
OMIT_REPEATED_TIMES=true
```

程式載入順序如下：

1. `.env`
2. `.env.local`
3. 已設定於作業系統的環境變數；作業系統環境變數優先且不會被覆蓋

### 資料庫設定

| 變數 | 說明 | 預設值 |
|---|---|---|
| `DB_HOST` | PostgreSQL 主機 | `localhost` |
| `DB_PORT` | PostgreSQL 連接埠 | `5432` |
| `DB_NAME` | 資料庫名稱 | `python_db` |
| `DB_USER` | 資料庫使用者 | `python_user` |
| `DB_PASSWORD` | 資料庫密碼 | 無預設值 |

密碼可以包含一般空白字元或特殊字元。含空格時建議使用雙引號：

```dotenv
DB_PASSWORD="my secret password"
```

`.env`、`.env.*` 都已列入 `.gitignore`；`.env.example` 例外並可提交。請勿將真實密碼寫入 `.env.example` 或版本控制。

### 終端機日誌設定

`CONSOLE_RUN_ID_MODE` 控制終端機中的 run ID 顯示方式：

- `once`：執行開始前印一次 `Run ID`，後續訊息不重複顯示。
- `every`：每則終端機日誌都顯示 `[run=<run_id>]`。

預設值為 `once`。

`OMIT_REPEATED_TIMES` 控制 Rich終端機是否省略連續重複的時間：

- `true`：省略連續重複的時間（預設）。
- `false`：每則終端機訊息都顯示時間。

值只接受 `true` 或 `false`，大小寫不區分。

終端機和日誌檔都會記錄執行結果。日誌檔 `logs/pipeline.log` 的每筆紀錄都會包含 run ID；結束分隔線只顯示原始文字。

## 資料庫資料表

資料庫需預先建立：

- `public.orders`：至少包含 `order_item_id`、`order_id`、`unit_price`、`quantity` 和 `status`。
- `public.data_quality_issue_log`：包含 `order_item_id`、`order_id`、`issue_type` 和 `issue_description`。

`public.data_quality_issue_log` 的 `(order_item_id, issue_type)` 應設定唯一限制，以便重複執行時略過已存在的異常。

## 執行

確認環境設定及資料表已備妥後，在專案根目錄執行：

```bash
python main.py
```

一次執行會依序完成 Extract、Transform、Load 與 Report。每次執行新增的異常筆數會顯示於終端機；相同資料及異常類型已存在時，不會重複新增。

### 報表輸出

每次執行會建立：

```text
reports/data_quality_YYYYMMDD_<run_id>.json
```

報表包含原始資料筆數、有效資料筆數、異常資料筆數、異常項目數量、有效率、異常率、本次新增筆數，以及處理時間資訊。

- `valid_rate` 與 `invalid_rate` 以百分比表示並四捨五入至小數點後兩位。
- `invalid_records` 是有異常的不同 `order_item_id` 數量。
- `issue_count` 是異常紀錄總數。
- `inserted_count` 是本次實際新增到資料庫的筆數。
- `processing_time` 記錄含時區的 `started_at`、`finished_at`、總耗時 `duration_seconds`，以及 extract、transform、load 各階段的耗時（秒）。總耗時涵蓋 ETL 階段，不含報表產生與寫檔時間。

## 測試

測試使用 Python 內建的 `unittest`，不需要連接 PostgreSQL：

```bash
python -m unittest discover -s tests -v
```

執行單一測試模組：

```bash
python -m unittest discover -s tests -p "test_transform.py" -v
python -m unittest discover -s tests -p "test_extract.py" -v
python -m unittest discover -s tests -p "test_etl_logging.py" -v
python -m unittest discover -s tests -p "test_db.py" -v
```

資料庫載入需要透過 `python main.py` 執行完整流程。

## 專案結構

```text
.
├── main.py            # Pipeline CLI 入口
├── pipeline.py        # ETL Pipeline 編排
├── config/
│   └── settings.py    # 環境變數設定
├── etl/
│   ├── extract.py     # 擷取訂單資料
│   └── load.py        # 寫入異常紀錄
├── quality/
│   └── rules.py       # 資料品質規則與營收計算
├── reporting/
│   └── quality_report.py # 品質報表統計與儲存
├── infrastructure/
│   ├── database.py    # PostgreSQL 連線與設定驗證
│   └── paths.py       # 檔案與目錄路徑工具
├── logging_setup/
│   ├── setup.py       # 設定與啟用日誌處理器
│   ├── common.py      # 共用格式器與 run ID filter
│   ├── console_handler.py
│   └── file_handler.py
├── .env.example       # 環境設定範本
└── tests/             # unittest 測試
```
