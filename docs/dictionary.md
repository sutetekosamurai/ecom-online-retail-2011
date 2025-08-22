# Data Dictionary — Online Retail 2011

## 0. Scope & Grain
- **Grain（明細）**: 1行 = 1商品の請求明細（InvoiceNo × StockCode）
- **期間**: 2010-12–2011-12（最終月は未完備の可能性）
- **通貨**: £（British Pound）

## 1. Cleaning Rules
- 返品除外: `InvoiceNo` が "C" 始まりは除外
- 量・単価: `Quantity > 0` かつ `UnitPrice >= 0`
- 顧客ID: `CustomerID` 欠損は除外
- 変換: `InvoiceDate` を日付/時刻へ変換（異常値は除外）

## 2. Processed Files
- `data/processed/transactions.parquet`  
  明細の最小列のみ（集計の基礎）
- `data/processed/cohort_retention.csv`  
  コホート（月×経過月）の継続率
- `data/processed/rfm_features.csv`  
  顧客ごとの R/F/M 指標とスコア
- `data/processed/ltv_customer_month.csv`  
  顧客×月の売上と累積LTV
- `data/processed/channel_month.csv`  
  **国をチャネル代理**とみなした月次集計

## 3. Field Definitions (transactions)
| Field | Type | Description |
|---|---|---|
| `InvoiceNo` | string | 請求番号（返品は “C” 始まり、今回除外） |
| `order_date` | date | 受注日（`InvoiceDate` の日付） |
| `order_month` | date | 月初日（Month粒度） |
| `customer_id` | string | 顧客ID（欠損除外・数値→文字） |
| `country` | string | 国名（チャネル代理） |
| `StockCode` | string | 商品コード |
| `Description` | string | 商品名 |
| `Quantity` | int | 購入数量（正値のみ） |
| `UnitPrice` | double | 単価（£、0以上） |
| `revenue` | double | 金額 = `Quantity * UnitPrice` |

## 4. KPI Definitions (Dashboard)
- **Revenue (£)** = Σ `revenue`
- **Orders (count)** = COUNTD(`InvoiceNo`)
- **Customers (count)** = COUNTD(`customer_id`)
- **UK Share (%)** = `Revenue where country='United Kingdom' / Revenue total`（同じ期間内）
- **Retention Rate (%)** = `active_users / base_users`  
  - `active_users`: コホート月から `cohort_index` ヶ月目に購入したユニーク顧客数  
  - `base_users`: `cohort_index = 0` のユニーク顧客数
- **RFM**  
  - `recency (days)`: スナップショット最終日 − 顧客の最新購入日  
  - `frequency` : COUNTD(`InvoiceNo`)（顧客単位）  
  - `monetary (£)`: Σ `revenue`（顧客単位）  
  - スコア: R/F/M を五分位で 1–5 に割当、`RFM_score = R+F+M`
- **LTV（Avg/Median）**（月次）  
  - `ltv_customer_month.csv` の `ltv_cum` を顧客×月で算出  
  - ダッシュボードで月ごとに **平均** / **中央値** を切替表示  
  - IQR: 25–75 パーセンタイル帯

## 5. Tableau Params / Calc（主要）
- **[Metric]**（Parameter）: `Revenue / Orders / Customers / UK Share`
- **[Metric Value]**（Calc）: 選択に応じて `SUM([revenue])` / `COUNTD([InvoiceNo])` / `COUNTD([customer_id])` / `UK Share` を返す
- **[Metric Prefix]/[Metric Unit]**: £ / orders / people / % を付加（ツールチップに使用）

## 6. Caveats
- 最終月は未完備の可能性（物流の遅延・記帳タイミング）。ダッシュボード上にも注記。
- 国=チャネルは**代理変数**。真のマーケチャネルが欲しい場合は後日 `marketing_spend.csv` を結合。

## 7. License / Source
- **Data**: UCI Machine Learning Repository — *Online Retail 2011* (**CC BY 4.0**)  
- **Code**: MIT（本リポジトリのスクリプト）
