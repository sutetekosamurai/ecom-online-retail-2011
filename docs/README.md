0. 実行環境
## Environment

- OS: Windows 11 / macOS 14 (どちらでもOK)
- Python: 3.11.9
- Tableau Desktop: 2025.2（以上）

### Python packages (pinned)
# requirements.txt を同梱
pandas==2.2.2
pyarrow==16.1.0
numpy==1.26.4

### Setup
python -m venv .venv
# Win
. .\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt

1. プロジェクト構成

analytics-lab/
└─ projects/
   └─ ecom-online-retail-2011/
      ├─ data/
      │  ├─ raw/                      # 生データ (例: Online Retail.csv)
      │  └─ processed/                # 前処理出力（自動生成）
      │     ├─ transactions.parquet
      │     ├─ cohort_retention.csv
      │     ├─ rfm_features.csv
      │     ├─ ltv_customer_month.csv
      │     └─ channel_month.csv
      ├─ dashboards/
      │  └─ tableau/
      │     ├─ 01_Country_Trends.twbx
      │     ├─ 02_EC_Core_Overview.twbx
      │     └─ 03_EC_Core_Customer.twbx
      ├─ docs/
      │  ├─ README.md   ← 本ファイル（リポのトップでも可）
      │  └─ data_dictionary.md
      ├─ notebooks/
      ├─ scripts/
      │  └─ 01_build_transactions.py
      ├─ sql/
      └─ requirements.txt

2. 再現手順 (Quick Start)
2.1 環境セットアップ
# Windows PowerShell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

2.2 データ配置
data/raw/ に生データを配置
例: Online Retail.csv（列：InvoiceNo, InvoiceDate, CustomerID, Country, StockCode, Description, Quantity, UnitPrice）

2.3 前処理実行
python scripts/01_build_transactions.py
・生成物（data/processed/）
・transactions.parquet … 明細（注文×商品）
・cohort_retention.csv … コホート別アクティブ率
・rfm_features.csv … 顧客別 R/F/M + スコア
・ltv_customer_month.csv … 顧客×月の累積 LTV
・channel_month.csv … 月×国（チャネル相当）の売上/注文/顧客

2.4 ダッシュボードの閲覧
 Tableau で以下を開く（*.twbx はデータ同梱型）：
  dashboards/tableau/01_Country_Trends.twbx
  dashboards/tableau/02_EC_Core_Overview.twbx
  dashboards/tableau/03_EC_Core_Customer.twbx

3. データ処理ルール（クリーニング）
  ・返品除外：InvoiceNo が C 始まりの行を除外
  ・数値クレンジング：Quantity > 0 かつ UnitPrice >= 0
  ・顧客ID欠損は除外（分析の一貫性）
  ・追加列
    〇revenue = Quantity * UnitPrice
    〇order_date = DATE(InvoiceDate)
    〇order_month = month start of InvoiceDate
    〇customer_id = str(int(CustomerID)), country = str(Country)
 
4. ダッシュボード概要
 01. EC Core — Overview
  KPI：Revenue / Orders / Customers / UK Share
  左：総量推移（絶対値）
  右：小さな倍数（国ごと独立軸）
  パラメータ：Metric（指標切替） / Top N Countries（この画面のみ使用）
 02. EC Core — Customer
  Cohort Heatmap：Retention Rate (%)×Cohort Index
  R×F Heatmap：Color = Log10(Avg Monetary [£/customer])、Label = Customers (count)
  LTV：平均（実線）・中央値（破線）・IQR（帯）
  アクション：R×F → LTV（Hover フィルター）
  ※ 本画面に Top N Countries フィルターは置かない（連動の安定性のため)
 03. 成果物
 ## Dashboards (Tableau Public)
- Live demo: https://public.tableau.com/…/OnlineRetail2011CountryCustomerAnalytics

### Country Trends — Customers
![Country Trends (PC)](dashboards/img/country_trends_pc.png)

### Customer Analytics — Cohort · R×F · LTV
![Customer Analytics (PC)](dashboards/img/customer_analytics_pc.png)

<details><summary>Mobile layout</summary>

![Country Trends (Phone)](dashboards/img/country_trends_phone.png)
![Customer Analytics (Phone)](dashboards/img/customer_analytics_phone.png)

</details>


5. 指標定義（抜粋）
※詳細は docs/data_dictionary.md を参照。
 ・Revenue (£)：Σ(Quantity × UnitPrice)
 ・Orders：COUNTD(InvoiceNo)
 ・Customers：COUNTD(customer_id)
 ・UK Share (%)：選択期間における UK / All countries（TopN非依存）
 ・Retention Rate：active_users / base_users
 ・Avg/Median LTV (£)：ltv_customer_month から集計
 ・IQR：25–75パーセンタイル帯
 
 6.スクリプト一覧
  ファイル名：scripts/01_build_transactions.py
  役割：生データ取り込み→前処理→各集計を生成
  入力：data/raw/*.csv
  出力：data/processed/*.csv, *.parquet

7. よくあるエラーと対処法
 ・CSVが見つからない：data/raw/ 配下に CSV が無い。ファイル名と拡張子を確認
 ・UnicodeDecodeError：読み込み時 encoding="unicode_escape" を維持／変換
 ・Tableauのリンク切れ：ライブ接続の *.twb を使う場合は data/processed/ を再指定
 ・R×F→LTVが反応しない：顧客ゼロのセルは仕様。もしくは LTV シートの［詳細］に Recency Rank / Frequency Rank があるか確認

8. 運用メモ
 ・連番命名（01_*）で処理順を明確化
 ・.venv/ は Git 管理外、環境再現は requirements.txt で
 ・データは原則 Git に含めない（data/raw・data/processed を .gitignore）

9. ライセンス / クレジット
 ・データ出所：https://archive.ics.uci.edu/dataset/352/online+retail
 ・ライセンス: Creative Commons Attribution 4.0 International (CC BY 4.0)
 （出典表示を条件に、共有・改変が可能）
----------------------------------------------------------------------------------------------------------------------------
本プロジェクトは UCI Machine Learning Repository の Online Retail データセットを使用しています。
引用: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
↪ このリポジトリでは 生データは再配布していません。
　UCI のページからダウンロードし、data/raw/ 配下に配置してください。
----------------------------------------------------------------------------------------------------------------------------

10. 変更履歴
 ・2025/08/22 初期リリース（前処理 + ３ダッシュボード）