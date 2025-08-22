import pandas as pd
from pathlib import Path


# === paths ===
ROOT = Path(__file__).resolve().parents[1]
raw_dir  = ROOT / "data" / "raw"
proc_dir = ROOT / "data" / "processed"
proc_dir.mkdir(parents=True, exist_ok=True)

# pick CSV
candidates = list(raw_dir.glob("*.csv"))
if not candidates:
    raise FileNotFoundError(f"No CSV found under: {raw_dir}")
csv_path = next((p for p in candidates if p.name == "Online Retail.csv"), candidates[0])

# === load & clean ===
df = pd.read_csv(csv_path, encoding="unicode_escape")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df = df.dropna(subset=["InvoiceDate"])
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] >= 0)]
df = df.dropna(subset=["CustomerID"]).copy()

df["revenue"] = df["Quantity"] * df["UnitPrice"]
df["order_date"]  = df["InvoiceDate"].dt.date
df["order_month"] = df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
df["customer_id"] = df["CustomerID"].astype(int).astype(str)
df["country"]     = df["Country"].astype(str)

transactions = df[[
  "InvoiceNo","order_date","order_month","customer_id","country",
  "StockCode","Description","Quantity","UnitPrice","revenue"
]]
transactions.to_parquet(proc_dir/"transactions.parquet", index=False)

# Cohort / Retention
first_month = transactions.groupby("customer_id")["order_month"].min().rename("cohort_month")
cohort = transactions.merge(first_month, on="customer_id", how="left")
def offset(m1, m2): return (m1.dt.year - m2.dt.year)*12 + (m1.dt.month - m2.dt.month)
cohort["cohort_index"] = offset(cohort["order_month"], cohort["cohort_month"])
cohort_users = (cohort.groupby(["cohort_month","cohort_index"])["customer_id"]
                      .nunique().reset_index(name="active_users"))
base = cohort_users.query("cohort_index == 0")[["cohort_month","active_users"]]\
       .rename(columns={"active_users":"base_users"})
retention = cohort_users.merge(base, on="cohort_month")
retention["retention_rate"] = retention["active_users"]/retention["base_users"]
retention.to_csv(proc_dir/"cohort_retention.csv", index=False)

# RFM
snapshot = pd.to_datetime(transactions["order_date"]).max()
rfm = (transactions.groupby("customer_id")
         .agg(recency=("order_date", lambda s: (pd.to_datetime(snapshot) - pd.to_datetime(s).max()).days),
              frequency=("InvoiceNo","nunique"),
              monetary=("revenue","sum"))
         .reset_index())
rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5,4,3,2,1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_score"] = rfm[["R","F","M"]].sum(axis=1)
rfm.to_csv(proc_dir/"rfm_features.csv", index=False)

# LTV monthly cum
rev_month = (transactions.groupby(["customer_id","order_month"])["revenue"]
                         .sum().reset_index().sort_values(["customer_id","order_month"]))
rev_month["ltv_cum"] = rev_month.groupby("customer_id")["revenue"].cumsum()
rev_month.to_csv(proc_dir/"ltv_customer_month.csv", index=False)

# Channel trend (country as proxy)
channel_month = (transactions.groupby(["order_month","country"])
                   .agg(orders=("InvoiceNo","nunique"),
                        customers=("customer_id","nunique"),
                        revenue=("revenue","sum"))
                   .reset_index())
channel_month.to_csv(proc_dir/"channel_month.csv", index=False)

print("Done. Outputs saved in data/processed/")
