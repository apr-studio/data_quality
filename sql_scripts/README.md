# SQL 腳本與範例資料使用手冊

本資料夾包含建立 ETL 所需資料表的 PostgreSQL SQL 檔，以及可匯入的訂單與異常紀錄範例 CSV。建議從專案根目錄依照本手冊操作。

## 檔案一覽

| 檔案 | 用途 |
|---|---|
| `orders.sql` | 建立 `public.orders` 訂單明細表。 |
| `insert_orders.csv` | `public.orders` 的 10 筆範例訂單明細；檔案沒有標題列。 |
| `data_quality_issue_log.sql` | 建立 `public.data_quality_issue_log` 異常紀錄表及防止同一明細重複記錄同類異常的唯一索引。 |
| `insert_data_quality_issue_log.csv` | 3 筆範例異常紀錄；檔案沒有標題列。 |

## 資料表與欄位

### `public.orders`

由 `orders.sql` 建立，供 Pipeline 擷取及檢查。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `order_item_id` | `bigint` | 主鍵、identity 自動編號；範例 CSV 提供明確 ID。 |
| `order_id` | `varchar(20)` | 訂單編號。 |
| `order_date` | `date` | 訂單日期。 |
| `customer_id` | `varchar(20)` | 顧客編號。 |
| `product_id` | `varchar(20)` | 商品編號。 |
| `product_name` | `varchar(100)` | 商品名稱。 |
| `quantity` | `integer` | 商品數量。 |
| `unit_price` | `numeric(12,2)` | 商品單價；CSV 中的空欄會匯入為 `NULL`。 |
| `status` | `varchar(20)` | 訂單狀態，例如 `Completed` 或 `Cancelled`。 |

### `public.data_quality_issue_log`

由 `data_quality_issue_log.sql` 建立，存放 Pipeline 偵測到的異常。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `issue_id` | `bigint` | 主鍵、identity 自動編號；範例 CSV 提供明確 ID。 |
| `order_item_id` | `bigint` | 對應訂單明細 ID。 |
| `order_id` | `varchar(20)` | 訂單編號。 |
| `issue_type` | `varchar(50)` | 異常類型。 |
| `issue_description` | `text` | 異常說明。 |
| `detected_at` | `timestamp` | 偵測時間；未提供時資料庫預設為目前時間。 |

此表另有唯一索引 `uq_issue_item_type`，限制相同 `order_item_id` 與 `issue_type` 不可重複。

## 初次建置與匯入

### 1. 連線至 PostgreSQL

在專案根目錄開啟終端機，使用你的資料庫連線資訊啟動 `psql`：

```bash
psql -h localhost -p 5432 -U <DB_USER> -d <DB_NAME>
```

將 `<DB_USER>` 和 `<DB_NAME>` 換成實際值。連線成功後，以下命令都在 `psql` 提示字元中執行。

### 2. 建立資料表

```psql
\i sql_scripts/orders.sql
\i sql_scripts/data_quality_issue_log.sql
```

兩份 SQL 使用 `CREATE TABLE IF NOT EXISTS`，可用於建立尚不存在的表；它們不會替既有資料表補上或修改欄位。SQL 中的表格擁有者指定為 `elena`，若資料庫沒有此角色或目前帳號無權變更擁有者，請先建立該角色，或依照環境調整 SQL 中的 `ALTER TABLE ... OWNER TO elena`。

### 3. 匯入範例 CSV

先匯入訂單，再匯入異常紀錄。`\copy` 由執行 `psql` 的本機讀取 CSV，以下路徑以專案根目錄為基準：

```psql
\copy public.orders (order_item_id, order_id, order_date, customer_id, product_id, product_name, quantity, unit_price, status) FROM 'sql_scripts/insert_orders.csv' WITH (FORMAT csv, NULL '', ENCODING 'UTF8');
\copy public.data_quality_issue_log (issue_id, order_item_id, order_id, issue_type, issue_description, detected_at) FROM 'sql_scripts/insert_data_quality_issue_log.csv' WITH (FORMAT csv, NULL '', ENCODING 'UTF8');
```

匯入時明確列出欄位，因為 CSV 沒有標題列，且欄位順序必須與命令中的欄位清單一致。`NULL ''` 會將空白 CSV 欄位（範例訂單中的單價）轉成 SQL `NULL`。

兩個 ID 欄位在資料表中都是 `GENERATED ALWAYS AS IDENTITY`。PostgreSQL 的 `COPY` 接受輸入的 identity 值；匯入後請同步 identity sequence，避免後續新增資料時產生已使用過的 ID：

```sql
SELECT setval(
    pg_get_serial_sequence('public.orders', 'order_item_id'),
    COALESCE(MAX(order_item_id), 1),
    COUNT(*) > 0
)
FROM public.orders;

SELECT setval(
    pg_get_serial_sequence('public.data_quality_issue_log', 'issue_id'),
    COALESCE(MAX(issue_id), 1),
    COUNT(*) > 0
)
FROM public.data_quality_issue_log;
```

以上建置與匯入步驟適用於空表。CSV 含有固定主鍵，再次匯入會遇到主鍵重複錯誤；請勿把它當成可重複執行的增量載入方式。若資料表已有正式資料，請先確認匯入 ID 不衝突，並避免覆蓋或清除既有資料。

## 範例資料內容

`insert_orders.csv` 包含 10 筆明細，其中有三筆刻意保留的異常資料：

- `order_item_id = 7`：訂單狀態為 `Cancelled`。
- `order_item_id = 8`：`unit_price` 空白，匯入後為 `NULL`。
- `order_item_id = 10`：`quantity` 為 `-1`。

`insert_data_quality_issue_log.csv` 預先記錄上述三筆異常，依序是 `Cancelled Order`、`Missing Unit Price` 和 `Invalid Quantity`。如果先匯入這份 CSV，再執行 Pipeline，唯一索引會避免這三種相同異常被再次寫入。

## 確認匯入結果

在 `psql` 執行：

```sql
SELECT COUNT(*) AS order_count FROM public.orders;
SELECT COUNT(*) AS issue_count FROM public.data_quality_issue_log;

SELECT order_item_id, order_id, quantity, unit_price, status
FROM public.orders
ORDER BY order_item_id;

SELECT order_item_id, order_id, issue_type, issue_description, detected_at
FROM public.data_quality_issue_log
ORDER BY issue_id;
```

第一次匯入空表後，範例資料應有 10 筆訂單及 3 筆異常紀錄。

## 執行專案 ETL

完成資料表及範例資料匯入後，退出 `psql`（輸入 `\q`），並依照專案根目錄 `README.md` 設定 `.env.local` 的 PostgreSQL 連線資訊，再執行：

```bash
python main.py
```

Pipeline 會從 `public.orders` 擷取資料、檢查品質，並將新的異常寫入 `public.data_quality_issue_log`。`orders.sql` 中的 `order_date`、顧客與商品欄位會保留在資料表中；目前 Pipeline 主要檢查 `order_item_id`、`order_id`、`unit_price`、`quantity` 和 `status`。每次執行也會在 `reports/` 產生 JSON 品質報表。

## 注意事項

- SQL 內的 `DROP TABLE` 與 `DROP INDEX` 範例目前是註解，不會在執行時刪除資料。
- `CREATE TABLE IF NOT EXISTS` 不會清空或重設既有資料。
- CSV 匯入是初始範例資料，不是可安全重複執行的正式載入流程。
- `\copy` 是 `psql` 命令，不是一般 SQL；請在 `psql` 中執行，並確認相對路徑以專案根目錄為準。
