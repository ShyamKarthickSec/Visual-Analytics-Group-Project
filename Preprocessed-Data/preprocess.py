# ==============================================================
#  WDI Preprocessing Script (Nishanth – Economic Data Analysis)
# ==============================================================

import pandas as pd
import numpy as np

# ---------- Step 1: File Paths ----------
data_path = "ce0f13d9-ba3f-4150-8b8c-bdd9a04cec8f_Data.csv"
meta_path = "ce0f13d9-ba3f-4150-8b8c-bdd9a04cec8f_Series - Metadata.csv"

# ---------- Step 2: Load Data ----------
print("📥 Loading data ...")
df = pd.read_csv(data_path)

# ---------- Step 3: Define Indicators to Keep ----------
indicators = {
    "NY.GDP.MKTP.CD": "GDP",
    "NY.GDP.MKTP.KD.ZG": "GDP_Growth",
    "FP.CPI.TOTL.ZG": "Inflation",
    "SL.UEM.TOTL.NE.ZS": "Unemployment",
    "NE.TRD.GNFS.ZS": "Trade",
    "GC.DOD.TOTL.GD.ZS": "Debt",
    "FS.AST.PRVT.GD.ZS": "Credit_to_Private_Sector",
    "FB.AST.NPER.ZS": "NPLs"
}

df = df[df["Series Code"].isin(indicators.keys())].copy()
print(f"✅ Retained {df['Series Code'].nunique()} target indicators")

# ---------- Step 4: Melt Wide → Long ----------
year_cols = [c for c in df.columns if "[YR" in c]
df_long = df.melt(
    id_vars=["Country Name", "Country Code", "Series Name", "Series Code"],
    value_vars=year_cols,
    var_name="Year",
    value_name="Value"
)

# Clean year column (remove [YRXXXX])
df_long["Year"] = df_long["Year"].str.extract(r"(\d{4})").astype(int)

# ---------- Step 5: Replace missing & convert values ----------
df_long["Value"] = df_long["Value"].replace("..", np.nan)
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

# Drop missing values
df_long = df_long.dropna(subset=["Value"])

# ---------- Step 6: Pivot to Country-Year Rows ----------
df_pivot = (
    df_long
    .pivot_table(
        index=["Country Name", "Country Code", "Year"],
        columns="Series Code",
        values="Value"
    )
    .reset_index()
)

# Rename columns based on mapping
df_pivot = df_pivot.rename(columns=indicators)

# ---------- Step 7: Optional Filtering ----------
df_pivot = df_pivot[df_pivot["Year"].between(1975, 2023)]

# ---------- Step 8: Final Cleaning ----------
df_pivot = df_pivot.dropna(how="all", subset=list(indicators.values()))
df_pivot = df_pivot.sort_values(["Country Name", "Year"]).reset_index(drop=True)

# ---------- Step 9: Save Cleaned Dataset ----------
output_file = "WDI_cleaned_1975_2023.csv"
df_pivot.to_csv(output_file, index=False)
print(f"✅ Saved cleaned dataset: {output_file}")
print(f"📊 Final shape: {df_pivot.shape}")

# ---------- Step 10: Quick Summary ----------
summary = df_pivot.describe(include="all")
print("\n📈 Summary Statistics:")
print(summary)
