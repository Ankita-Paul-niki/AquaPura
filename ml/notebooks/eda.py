"""
AquaPura — Phase 1: Exploratory Data Analysis (EDA)
====================================================

This script examines the Kaggle Water Potability dataset, computes summary
statistics, checks data quality, and saves charts + a JSON report to:

    ml/reports/eda_report.json
    ml/reports/figures/

HOW TO RUN (from the AquaPura root folder)
------------------------------------------
Step 1 — Activate your virtual environment (if you haven't already):
    .\\backend\\venv\\Scripts\\Activate.ps1          # Windows PowerShell

    If you haven't installed the ML packages yet, run:
    pip install pandas numpy matplotlib seaborn scikit-learn

Step 2 — Run the script:
    python ml/notebooks/eda.py

The script will print a readable summary to the terminal and save all
artefacts to ml/reports/.

⚠️  IMPORTANT DISCLAIMER
--------------------------
AquaPura is a preliminary screening tool only. Its predictions are based
on a single publicly available dataset and a statistical model. They do NOT
constitute certified water-quality testing and should NEVER be used as the
sole basis for drinking-water safety decisions. Always defer to accredited
laboratory analysis and local water-authority guidelines.
"""

import json
import sys
from pathlib import Path

# ── Resolve paths relative to project root ────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # ml/notebooks/
ROOT       = SCRIPT_DIR.parents[1]                    # AquaPura/
RAW_CSV    = ROOT / "dataset" / "raw" / "water_potability.csv"
REPORTS    = ROOT / "ml" / "reports"
FIGURES    = REPORTS / "figures"

# ── Guard: dataset must exist before anything else runs ──────────────────────
if not RAW_CSV.exists():
    print()
    print("=" * 65)
    print("  ⛔  Dataset not found.")
    print()
    print(f"  Expected: {RAW_CSV}")
    print()
    print("  Please download water_potability.csv from Kaggle and place")
    print("  it at:  dataset/raw/water_potability.csv")
    print()
    print("  URL: https://www.kaggle.com/datasets/adityakadiwal/water-potability")
    print("=" * 65)
    print()
    sys.exit(1)

# ── Imports (only after guard so the missing-file message is clean) ───────────
try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend — no display needed
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as exc:
    print(f"\n[ERROR] Missing dependency: {exc}")
    print("  Run:  pip install pandas numpy matplotlib seaborn")
    sys.exit(1)

# ── Styling ───────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
AQUA_PALETTE = ["#0284c7", "#f97316"]   # blue = potable, orange = not potable

FIGURES.mkdir(parents=True, exist_ok=True)

# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("\n" + "=" * 65)
print("  AquaPura — Exploratory Data Analysis")
print("=" * 65)

df = pd.read_csv(RAW_CSV)

print(f"\n[1] Loaded:  {RAW_CSV.name}")
print(f"    Rows:    {df.shape[0]:,}")
print(f"    Columns: {df.shape[1]}")

# =============================================================================
# 2. COLUMN NAMES & DATA TYPES
# =============================================================================
print("\n[2] Column names and data types")
print("-" * 40)
print(df.dtypes.to_string())

# Expected feature names (from the Kaggle dataset description)
EXPECTED_FEATURES = [
    "ph", "Hardness", "Solids", "Chloramines", "Sulfate",
    "Conductivity", "Organic_carbon", "Trihalomethanes", "Turbidity",
]
TARGET = "Potability"

# Validate the target column exists
if TARGET not in df.columns:
    print(f"\n[ERROR] Target column '{TARGET}' not found in the dataset.")
    print(f"  Columns present: {list(df.columns)}")
    sys.exit(1)

# Identify actual feature columns (everything except the target)
feature_cols = [c for c in df.columns if c != TARGET]
print(f"\n  Target column : {TARGET}")
print(f"  Feature columns ({len(feature_cols)}): {feature_cols}")

# Check for unexpected / missing columns
missing_expected = [c for c in EXPECTED_FEATURES if c not in df.columns]
extra_cols       = [c for c in feature_cols if c not in EXPECTED_FEATURES]
if missing_expected:
    print(f"\n  ⚠  Expected columns NOT found: {missing_expected}")
if extra_cols:
    print(f"\n  ℹ  Extra columns found (not in standard list): {extra_cols}")

# =============================================================================
# 3. DUPLICATE ROWS
# =============================================================================
print("\n[3] Duplicate rows")
print("-" * 40)
n_dupes = df.duplicated().sum()
print(f"  Duplicate rows: {n_dupes}")
if n_dupes > 0:
    print("  ⚠  Duplicates found. Consider removing them before training.")

# =============================================================================
# 4. MISSING VALUES
# =============================================================================
print("\n[4] Missing values per column")
print("-" * 40)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    "missing_count": missing,
    "missing_pct":   missing_pct,
}).sort_values("missing_pct", ascending=False)
print(missing_df[missing_df["missing_count"] > 0].to_string())
if missing_df["missing_count"].sum() == 0:
    print("  ✓  No missing values found.")
else:
    total_missing = missing_df["missing_count"].sum()
    print(f"\n  Total missing cells: {total_missing:,}")
    print("  ⚠  Do NOT silently drop or fill these during EDA.")
    print("     The imputation strategy will be decided in Phase 2.")

# ── Figure: missing-value heatmap ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))
missing_plot = missing_df[missing_df["missing_count"] > 0]["missing_pct"]
if not missing_plot.empty:
    missing_plot.plot(kind="barh", ax=ax, color="#0284c7")
    ax.set_xlabel("% Missing")
    ax.set_title("Missing Value Percentage by Column")
    ax.invert_yaxis()
    fig.tight_layout()
    out = FIGURES / "missing_values.png"
    fig.savefig(out, dpi=120)
    print(f"\n  → Saved chart: {out.relative_to(ROOT)}")
plt.close(fig)

# =============================================================================
# 5. SUMMARY STATISTICS
# =============================================================================
print("\n[5] Summary statistics (numerical features)")
print("-" * 40)
stats = df[feature_cols].describe().T
stats["skew"]     = df[feature_cols].skew()
stats["kurtosis"] = df[feature_cols].kurtosis()
pd.set_option("display.float_format", "{:.3f}".format)
pd.set_option("display.max_columns", 12)
print(stats.to_string())

# =============================================================================
# 6. TARGET DISTRIBUTION (CLASS BALANCE)
# =============================================================================
print("\n[6] Target distribution — Potability")
print("-" * 40)
class_counts = df[TARGET].value_counts().sort_index()
class_pct    = (class_counts / len(df) * 100).round(2)
class_labels = {0: "Not Potable (0)", 1: "Potable (1)"}
for val, cnt in class_counts.items():
    label = class_labels.get(val, str(val))
    print(f"  {label}: {cnt:,}  ({class_pct[val]:.1f}%)")

imbalance_ratio = class_counts.max() / class_counts.min()
print(f"\n  Imbalance ratio (majority / minority): {imbalance_ratio:.2f}")
if imbalance_ratio > 1.5:
    print("  ⚠  Moderate class imbalance detected.")
    print("     Consider class_weight='balanced' or SMOTE in Phase 2.")

# ── Figure: class balance bar ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(5, 4))
bars = ax.bar(
    [class_labels.get(v, str(v)) for v in class_counts.index],
    class_counts.values,
    color=AQUA_PALETTE,
    edgecolor="white",
    width=0.5,
)
for bar, pct in zip(bars, class_pct.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 30,
        f"{pct:.1f}%",
        ha="center", va="bottom", fontsize=11,
    )
ax.set_title("Potability Class Distribution")
ax.set_ylabel("Sample Count")
ax.set_ylim(0, class_counts.max() * 1.15)
fig.tight_layout()
out = FIGURES / "class_distribution.png"
fig.savefig(out, dpi=120)
print(f"\n  → Saved chart: {out.relative_to(ROOT)}")
plt.close(fig)

# =============================================================================
# 7. FEATURE DISTRIBUTIONS
# =============================================================================
print("\n[7] Feature distributions (histograms + KDE)")
print("-" * 40)

n_cols  = 3
n_rows  = -(-len(feature_cols) // n_cols)   # ceiling division
fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
axes = axes.flatten()

for i, col in enumerate(feature_cols):
    ax = axes[i]
    for cls_val, cls_label, color in [
        (0, "Not Potable", AQUA_PALETTE[1]),
        (1, "Potable",     AQUA_PALETTE[0]),
    ]:
        subset = df.loc[df[TARGET] == cls_val, col].dropna()
        ax.hist(
            subset, bins=40, alpha=0.5, color=color,
            label=cls_label, density=True, edgecolor="none",
        )
    ax.set_title(col)
    ax.set_xlabel("")
    ax.set_ylabel("Density")
    ax.legend(fontsize=8)

# Hide any unused subplot panels
for j in range(len(feature_cols), len(axes)):
    axes[j].set_visible(False)

fig.suptitle("Feature Distributions by Potability Class", fontsize=14, y=1.01)
fig.tight_layout()
out = FIGURES / "feature_distributions.png"
fig.savefig(out, dpi=120, bbox_inches="tight")
print(f"  → Saved chart: {out.relative_to(ROOT)}")
plt.close(fig)

# =============================================================================
# 8. BOX PLOTS (outlier visualisation)
# =============================================================================
print("\n[8] Box plots (outlier visualisation)")
print("-" * 40)

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
axes = axes.flatten()

for i, col in enumerate(feature_cols):
    ax = axes[i]
    data_by_class = [
        df.loc[df[TARGET] == cls_val, col].dropna().values
        for cls_val in [0, 1]
    ]
    bp = ax.boxplot(
        data_by_class,
        tick_labels=["Not Potable", "Potable"],
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 1.5},
    )
    for patch, color in zip(bp["boxes"], AQUA_PALETTE[::-1]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.set_title(col)
    ax.set_ylabel("Value")

for j in range(len(feature_cols), len(axes)):
    axes[j].set_visible(False)

fig.suptitle("Box Plots by Potability Class", fontsize=14, y=1.01)
fig.tight_layout()
out = FIGURES / "box_plots.png"
fig.savefig(out, dpi=120, bbox_inches="tight")
print(f"  → Saved chart: {out.relative_to(ROOT)}")
plt.close(fig)

# =============================================================================
# 9. CORRELATION MATRIX
# =============================================================================
print("\n[9] Correlation matrix (numerical features)")
print("-" * 40)
corr = df[feature_cols + [TARGET]].corr()
print(corr.round(3).to_string())

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))   # show lower triangle only
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", center=0, linewidths=0.5,
    square=True, ax=ax,
    annot_kws={"size": 9},
)
ax.set_title("Feature Correlation Matrix", fontsize=13)
fig.tight_layout()
out = FIGURES / "correlation_matrix.png"
fig.savefig(out, dpi=120)
print(f"\n  → Saved chart: {out.relative_to(ROOT)}")
plt.close(fig)

# =============================================================================
# 10. PAIRWISE SCATTER (top 4 features by variance — kept manageable)
# =============================================================================
print("\n[10] Pairwise scatter (highest-variance features)")
print("-" * 40)
top4 = df[feature_cols].var().nlargest(4).index.tolist()
print(f"  Top-4 by variance: {top4}")
pair_df = df[top4 + [TARGET]].copy()
pair_df[TARGET] = pair_df[TARGET].map({0: "Not Potable", 1: "Potable"})
pair_grid = sns.pairplot(
    pair_df, hue=TARGET, diag_kind="kde",
    plot_kws={"alpha": 0.35, "s": 15, "edgecolor": "none"},
    palette={"Not Potable": AQUA_PALETTE[1], "Potable": AQUA_PALETTE[0]},
)
pair_grid.fig.suptitle("Pairwise Scatter (Top-4 Variance Features)", y=1.02)
out = FIGURES / "pairplot_top4.png"
pair_grid.savefig(out, dpi=100)
print(f"  → Saved chart: {out.relative_to(ROOT)}")
plt.close("all")

# =============================================================================
# 11. SAVE JSON REPORT
# =============================================================================
print("\n[11] Saving EDA report to ml/reports/eda_report.json")
print("-" * 40)

def _safe(val):
    """Convert numpy/pandas scalars to native Python for JSON serialisation."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return None if (isinstance(val, float) and np.isnan(val)) else float(round(val, 6))
    return val

report = {
    "dataset": {
        "source": "Kaggle — Water Potability (adityakadiwal)",
        "url": "https://www.kaggle.com/datasets/adityakadiwal/water-potability",
        "raw_file": str(RAW_CSV.relative_to(ROOT)),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
    },
    "target": {
        "column": TARGET,
        "class_counts": {
            str(k): _safe(v) for k, v in class_counts.items()
        },
        "class_percentages": {
            str(k): _safe(v) for k, v in class_pct.items()
        },
        "imbalance_ratio": _safe(imbalance_ratio),
    },
    "features": {
        "columns": feature_cols,
        "missing_values": {
            col: {
                "count": _safe(missing[col]),
                "pct":   _safe(missing_pct[col]),
            }
            for col in feature_cols
        },
    },
    "duplicates": {
        "count": int(n_dupes),
    },
    "summary_statistics": {
        col: {
            "count":  _safe(stats.loc[col, "count"]),
            "mean":   _safe(stats.loc[col, "mean"]),
            "std":    _safe(stats.loc[col, "std"]),
            "min":    _safe(stats.loc[col, "min"]),
            "25pct":  _safe(stats.loc[col, "25%"]),
            "50pct":  _safe(stats.loc[col, "50%"]),
            "75pct":  _safe(stats.loc[col, "75%"]),
            "max":    _safe(stats.loc[col, "max"]),
            "skew":   _safe(stats.loc[col, "skew"]),
            "kurtosis": _safe(stats.loc[col, "kurtosis"]),
        }
        for col in feature_cols
    },
    "correlations_with_target": {
        col: _safe(corr.loc[col, TARGET])
        for col in feature_cols
    },
    "figures_saved": [str(p.relative_to(ROOT)) for p in sorted(FIGURES.glob("*.png"))],
    "disclaimer": (
        "AquaPura is a preliminary screening tool only. "
        "These results do not constitute certified water-quality testing "
        "and must not be used as the sole basis for drinking-water safety decisions."
    ),
}

report_path = REPORTS / "eda_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"  → Saved: {report_path.relative_to(ROOT)}")

# =============================================================================
# 12. FINAL SUMMARY
# =============================================================================
print()
print("=" * 65)
print("  EDA COMPLETE — Summary")
print("=" * 65)
print(f"  Rows             : {df.shape[0]:,}")
print(f"  Features         : {len(feature_cols)}")
print(f"  Target           : {TARGET}")
print(f"  Duplicate rows   : {n_dupes}")
print(f"  Total missing    : {int(missing.sum()):,} cells across "
      f"{int((missing > 0).sum())} column(s)")
for val, cnt in class_counts.items():
    print(f"  Class {val} ({class_labels[val]:<20s}): "
          f"{cnt:,}  ({class_pct[val]:.1f}%)")
print(f"  Imbalance ratio  : {imbalance_ratio:.2f}")
print()
print("  Artefacts written to  ml/reports/")
print("  Next step → Phase 2: preprocessing decisions")
print("              See docs/ml_pipeline.md for guidance")
print()
print("  ⚠️  DISCLAIMER: AquaPura provides preliminary screening only.")
print("     It does not replace certified laboratory water-quality testing.")
print("=" * 65)
print()
