"""
A/B test project, step 1: load the Cookie Cats data and check its quality.

Put this file in the same folder as cookie_cats.csv, then run:
    python 01_load_and_check.py
Needs: pandas (pip install pandas)
"""
import math
import pandas as pd

df = pd.read_csv("cookie_cats.csv")

print("=== 1. SHAPE AND COLUMNS ===")
print(f"Rows: {len(df):,}")
print(df.dtypes.to_string())
print(df.head().to_string(index=False))

print("\n=== 2. DATA QUALITY ===")
print(f"Duplicate userids: {df['userid'].duplicated().sum()}")
print(f"Missing values: {int(df.isna().sum().sum())}")
print(f"Players with 0 game rounds: {(df['sum_gamerounds'] == 0).sum():,} "
      f"({(df['sum_gamerounds'] == 0).mean():.1%})")

print("\n=== 3. GROUP SIZES (was the split fair?) ===")
counts = df["version"].value_counts().sort_index()
print(counts.to_string())
n = counts.sum()
expected = n / 2
chi2 = sum((c - expected) ** 2 / expected for c in counts)
p_srm = math.erfc(math.sqrt(chi2 / 2))   # p-value for 1 degree of freedom
print(f"Expected for a 50/50 split: {expected:,.0f} each")
print(f"Chi-square = {chi2:.2f}, p = {p_srm:.4f}")
if p_srm < 0.05:
    print("-> The groups are slightly unequal more often than chance would "
          "explain. Note this as a limitation (possible sample-ratio mismatch).")
else:
    print("-> Group sizes look consistent with a fair 50/50 split.")

print("\n=== 4. GAME ROUNDS: LOOK FOR OUTLIERS ===")
print(df["sum_gamerounds"].describe().round(1).to_string())
print("\nTop 5 players by rounds played:")
print(df.nlargest(5, "sum_gamerounds").to_string(index=False))

print("\n=== 5. FIRST LOOK AT RETENTION (not a test yet) ===")
summary = df.groupby("version").agg(
    players=("userid", "count"),
    retention_1=("retention_1", "mean"),
    retention_7=("retention_7", "mean"),
    median_rounds=("sum_gamerounds", "median"),
)
summary["retention_1"] = (summary["retention_1"] * 100).round(2)
summary["retention_7"] = (summary["retention_7"] * 100).round(2)
print(summary.to_string())
print("\nThese are just percentages. The next step is to test whether the "
      "differences are real or could be luck.")
