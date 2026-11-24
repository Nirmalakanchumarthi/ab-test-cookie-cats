"""
A/B test project, step 3: export the results as small CSV files for the dashboard.

Run in the same folder as cookie_cats.csv:
    python 03_export_results.py
Makes: results_summary.csv and results_difference.csv
Needs: pandas (numpy comes with it)
"""
import math
import pandas as pd

df = pd.read_csv("cookie_cats.csv")
control = df[df["version"] == "gate_30"]
treat = df[df["version"] == "gate_40"]
ALPHA_STRICT = 0.025        # 0.05 split across two tests (Bonferroni)

# ---- File 1: one row per version (for the bar chart) ----
clean = df[df["sum_gamerounds"] < 10_000]       # drops the 49,854-round outlier
summary = df.groupby("version").agg(
    players=("userid", "count"),
    retention_1_pct=("retention_1", "mean"),
    retention_7_pct=("retention_7", "mean"),
).reset_index()
summary["retention_1_pct"] = (summary["retention_1_pct"] * 100).round(2)
summary["retention_7_pct"] = (summary["retention_7_pct"] * 100).round(2)
summary["median_rounds"] = summary["version"].map(
    clean.groupby("version")["sum_gamerounds"].median())
summary.to_csv("results_summary.csv", index=False)

# ---- File 2: one row per metric (difference, interval, p-value) ----
rows = []
for col, label in [("retention_1", "Day-1 retention"), ("retention_7", "Day-7 retention")]:
    x1, n1 = int(control[col].sum()), len(control)
    x2, n2 = int(treat[col].sum()), len(treat)
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1
    pooled = (x1 + x2) / (n1 + n2)
    z = diff / math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    p_value = math.erfc(abs(z) / math.sqrt(2))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    real = p_value < ALPHA_STRICT
    rows.append({
        "metric": label,
        "gate_30_pct": round(p1 * 100, 2),
        "gate_40_pct": round(p2 * 100, 2),
        "difference_points": round(diff * 100, 2),
        "ci_low_points": round((diff - 1.96 * se) * 100, 2),
        "ci_high_points": round((diff + 1.96 * se) * 100, 2),
        "p_value": round(p_value, 4),
        "real_difference": "Yes" if real else "No (could be luck)",
    })
pd.DataFrame(rows).to_csv("results_difference.csv", index=False)

print(pd.read_csv("results_summary.csv").to_string(index=False))
print()
print(pd.read_csv("results_difference.csv").to_string(index=False))
print("\nSaved results_summary.csv and results_difference.csv")
