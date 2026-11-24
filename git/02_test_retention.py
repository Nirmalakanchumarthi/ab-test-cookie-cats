"""
A/B test project, step 2: are the retention differences real or just luck?

Run in the same folder as cookie_cats.csv:
    python 02_test_retention.py
Needs: pandas and numpy (numpy comes with pandas).

Control = gate_30 (the existing design). Treatment = gate_40 (the change).
Difference = gate_40 minus gate_30, so a NEGATIVE number means the change
retained fewer players.
"""
import math
import numpy as np
import pandas as pd

ALPHA = 0.05
rng = np.random.default_rng(42)          # fixed seed so results repeat

df = pd.read_csv("cookie_cats.csv")
control = df[df["version"] == "gate_30"]
treat = df[df["version"] == "gate_40"]


def normal_two_sided_p(z):
    return math.erfc(abs(z) / math.sqrt(2))


def test_retention(col, label):
    x1, n1 = int(control[col].sum()), len(control)
    x2, n2 = int(treat[col].sum()), len(treat)
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1

    # Two-proportion z-test (pooled standard error)
    pooled = (x1 + x2) / (n1 + n2)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = diff / se_pooled
    p_value = normal_two_sided_p(z)

    # 95% confidence interval for the difference (unpooled standard error)
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    lo, hi = diff - 1.96 * se, diff + 1.96 * se

    # Bootstrap check: resample each group 10,000 times.
    # For a yes/no outcome, resampling rows is the same as a binomial draw.
    boot = (rng.binomial(n2, p2, 10_000) / n2) - (rng.binomial(n1, p1, 10_000) / n1)
    b_lo, b_hi = np.percentile(boot, [2.5, 97.5])

    # Smallest difference this sample could reliably detect (80% power)
    mde = (1.96 + 0.84) * math.sqrt(2 * p1 * (1 - p1) / ((n1 + n2) / 2))

    print(f"\n=== {label} ===")
    print(f"gate_30: {p1:.2%}   gate_40: {p2:.2%}")
    print(f"Difference (gate_40 - gate_30): {diff * 100:+.2f} percentage points "
          f"({diff / p1:+.1%} relative)")
    print(f"95% CI for the difference: [{lo * 100:+.2f}, {hi * 100:+.2f}] points")
    print(f"Bootstrap 95% interval:    [{b_lo * 100:+.2f}, {b_hi * 100:+.2f}] points")
    print(f"z = {z:.2f}, p-value = {p_value:.4f}")
    print(f"Smallest difference this test can reliably detect: ~{mde * 100:.2f} points")
    return p_value


p1_val = test_retention("retention_1", "DAY-1 RETENTION")
p7_val = test_retention("retention_7", "DAY-7 RETENTION")

print("\n=== MULTIPLE TESTS ===")
print(f"Two tests were run, so a stricter cut-off is {ALPHA / 2:.3f} (Bonferroni).")
print(f"Day-1 significant at {ALPHA / 2:.3f}? {p1_val < ALPHA / 2}")
print(f"Day-7 significant at {ALPHA / 2:.3f}? {p7_val < ALPHA / 2}")

print("\n=== GAME ROUNDS (outlier removed) ===")
clean = df[df["sum_gamerounds"] < 10_000]
print(f"Removed {len(df) - len(clean)} player(s) with 10,000+ rounds "
      f"(max was {df['sum_gamerounds'].max():,}, next highest {clean['sum_gamerounds'].max():,}).")
for name, g in clean.groupby("version"):
    print(f"{name}: mean {g['sum_gamerounds'].mean():.1f}, "
          f"median {g['sum_gamerounds'].median():.0f}")
print("Medians are the safer comparison because a few very heavy players skew the mean.")
