"""
AquaPura — Phase 1: Data Preprocessing
=======================================

What this script does
---------------------
1. Reads the raw CSV from dataset/raw/water_potability.csv.
2. Removes exact duplicate rows (there are none in this dataset, but the
   check is kept as a safeguard for future data refreshes).
3. Does NOT impute missing values — that step belongs inside the scikit-learn
   Pipeline in train.py so imputer statistics are fitted only on training data,
   preventing data leakage.
4. Does NOT cap outliers — the EDA showed no reason to do so.
5. Performs a reproducible stratified 80/20 train/test split on Potability so
   both sets preserve the ~61%/39% class ratio.
6. Writes dataset/processed/train.csv and dataset/processed/test.csv.
7. Saves a JSON summary to ml/reports/preprocessing_report.json.

The original raw CSV is NEVER modified.

HOW TO RUN
----------
    python ml/scripts/preprocess.py

Prerequisites: pandas (already in venv). Run AFTER eda.py.
"""

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT       = SCRIPT_DIR.parents[1]
RAW_CSV    = ROOT / "dataset" / "raw"       / "water_potability.csv"
TRAIN_CSV  = ROOT / "dataset" / "processed" / "train.csv"
TEST_CSV   = ROOT / "dataset" / "processed" / "test.csv"
REPORTS    = ROOT / "ml" / "reports"

# ── Configuration ──────────────────────────────────────────────────────────────
TARGET       = "Potability"
TEST_SIZE    = 0.20   # 20 % held-out test set
RANDOM_SEED  = 42     # fixed for full reproducibility

# ── Guard: raw dataset must exist ─────────────────────────────────────────────
if not RAW_CSV.exists():
    print(f"\n[ERROR] Raw dataset not found at: {RAW_CSV}")
    print("  Download it from Kaggle first — see docs/ml_pipeline.md.")
    sys.exit(1)

# ==============================================================================
print("\n" + "=" * 60)
print("  AquaPura — Preprocessing Pipeline")
print("=" * 60)

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW_CSV)
original_rows = len(df)
print(f"\n[1] Loaded {RAW_CSV.name}: {original_rows:,} rows × {df.shape[1]} columns")

# ── Step 1: Remove exact duplicate rows ───────────────────────────────────────
n_before   = len(df)
df         = df.drop_duplicates()
n_dupes    = n_before - len(df)
print(f"[2] Duplicates removed : {n_dupes}")

# ── Step 2: Report missing values (not imputed here) ──────────────────────────
print("\n[3] Missing values per column (NOT imputed — handled in train.py):")
missing_info = {}
for col in df.columns:
    n_miss = int(df[col].isnull().sum())
    pct    = round(n_miss / len(df) * 100, 2)
    missing_info[col] = {"count": n_miss, "pct": pct}
    flag = "  ** has missing **" if n_miss > 0 else ""
    print(f"  {col:<22s}: {n_miss:>4d}  ({pct:.2f}%){flag}")

# ── Step 3: Stratified train / test split ─────────────────────────────────────
X = df.drop(columns=[TARGET])
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_SEED,
    stratify=y,
)

train_df = X_train.copy()
train_df[TARGET] = y_train.values

test_df = X_test.copy()
test_df[TARGET] = y_test.values

print(f"\n[4] Stratified {int((1-TEST_SIZE)*100)}/{int(TEST_SIZE*100)} split  "
      f"(random_seed={RANDOM_SEED})")
print(f"  Train : {len(train_df):>5,} rows")
print(f"  Test  : {len(test_df):>5,} rows")

# Class distribution helper
def class_dist(series):
    counts = series.value_counts().sort_index()
    return {
        str(int(k)): {
            "count": int(v),
            "pct":   round(int(v) / len(series) * 100, 2),
        }
        for k, v in counts.items()
    }

train_dist = class_dist(train_df[TARGET])
test_dist  = class_dist(test_df[TARGET])

print("\n  Class distribution:")
print(f"    Train — class 0: {train_dist['0']['count']} "
      f"({train_dist['0']['pct']:.1f}%)  "
      f"class 1: {train_dist['1']['count']} "
      f"({train_dist['1']['pct']:.1f}%)")
print(f"    Test  — class 0: {test_dist['0']['count']}  "
      f"({test_dist['0']['pct']:.1f}%)  "
      f"class 1: {test_dist['1']['count']}  "
      f"({test_dist['1']['pct']:.1f}%)")

# ── Step 4: Save processed splits ─────────────────────────────────────────────
TRAIN_CSV.parent.mkdir(parents=True, exist_ok=True)
train_df.to_csv(TRAIN_CSV, index=False)
test_df.to_csv(TEST_CSV,   index=False)
print(f"\n[5] Saved: {TRAIN_CSV.relative_to(ROOT)}")
print(f"     Saved: {TEST_CSV.relative_to(ROOT)}")

# ── Step 5: Save preprocessing report ─────────────────────────────────────────
REPORTS.mkdir(parents=True, exist_ok=True)
report = {
    "original_shape":      {"rows": original_rows, "cols": df.shape[1]},
    "duplicates_removed":  n_dupes,
    "missing_values":      missing_info,
    "imputation":          "none — handled inside scikit-learn Pipeline in train.py",
    "outlier_capping":     "none — EDA showed no justification",
    "split": {
        "strategy":    "stratified",
        "test_size":   TEST_SIZE,
        "random_seed": RANDOM_SEED,
        "train_rows":  len(train_df),
        "test_rows":   len(test_df),
        "train_class_distribution": train_dist,
        "test_class_distribution":  test_dist,
    },
    "output_files": {
        "train": str(TRAIN_CSV.relative_to(ROOT)),
        "test":  str(TEST_CSV.relative_to(ROOT)),
    },
    "disclaimer": (
        "AquaPura is a preliminary screening tool only. "
        "Do not use these results as the sole basis for drinking-water "
        "safety decisions."
    ),
}
report_path = REPORTS / "preprocessing_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(f"[6] Saved report: {report_path.relative_to(ROOT)}")

print("\n  Done. Next step: Phase 2 model training  (ml/scripts/train.py)")
print("=" * 60)
