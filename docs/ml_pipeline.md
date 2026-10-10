# AquaPura — ML Pipeline

> **Status:** Phase 1 complete — EDA and preprocessing scripts finalised; splits generated.

> ⚠️ **Disclaimer:** AquaPura is a preliminary screening tool only. Predictions do not
> constitute certified water-quality testing and must not be used as the sole basis for
> drinking-water safety decisions. Always defer to accredited laboratory analysis.

---

## Dataset

| Property | Value |
|---|---|
| Source | [Kaggle — Water Potability (adityakadiwal)](https://www.kaggle.com/datasets/adityakadiwal/water-potability) |
| Licence | CC0: Public Domain |
| Raw file | `dataset/raw/water_potability.csv` — **never modified** |
| Train split | `dataset/processed/train.csv` — 80 % of data, stratified |
| Test split | `dataset/processed/test.csv` — 20 % of data, locked until final evaluation |
| Target column | `Potability` (0 = not potable, 1 = potable) |
| EDA script | `ml/notebooks/eda.py` |
| Preprocessing script | `ml/scripts/preprocess.py` |
| Training script | `ml/scripts/train.py` |
| EDA report | `ml/reports/eda_report.json` |
| Preprocessing report | `ml/reports/preprocessing_report.json` |

### Dataset facts (from EDA)

| Property | Value |
|---|---|
| Total rows | 3,276 |
| Columns | 10 (9 features + 1 target) |
| Duplicate rows | 0 |
| Class 0 (not potable) | 1,998 (61.0 %) |
| Class 1 (potable) | 1,278 (39.0 %) |
| Imbalance ratio | 1.56 : 1 (mild) |

### Missing values

| Column | Missing count | % missing |
|---|---|---|
| `ph` | 491 | 14.99 % |
| `Sulfate` | 781 | 23.84 % |
| `Trihalomethanes` | 162 | 4.95 % |
| All others | 0 | 0 % |

### Known dataset limitations

- **Missing values:** `ph`, `Sulfate`, and `Trihalomethanes` contain NaN. Imputation
  is handled inside the scikit-learn training Pipeline (see below) to prevent leakage.
- **Class imbalance:** More non-potable samples than potable. Addressed via
  `class_weight='balanced'` in classifier constructors — no SMOTE at this stage.
- **Synthetic/aggregated origin:** This is a compiled research dataset, not live
  field measurements. Real-world sensor readings vary by geography, season, and
  measurement method.
- **No temporal or geographic information:** Samples cannot be linked to a location
  or time period, limiting real-world applicability.
- **Label reliability:** The `Potability` label is not certified by any water authority.
  Use with caution and always pair with professional testing.
- **Low feature-target correlation:** All nine features have near-zero linear
  correlation with `Potability` (range −0.03 to +0.03), indicating this is a
  genuinely difficult classification problem.

---

## Features

| Column name | Unit | Description |
|---|---|---|
| `ph` | — | pH of water (0–14 scale; WHO safe range: 6.5–8.5) |
| `Hardness` | mg/L | Calcium and magnesium salt concentration |
| `Solids` | ppm | Total dissolved solids (TDS) |
| `Chloramines` | ppm | Disinfectant; safe up to ~4 ppm (EPA) |
| `Sulfate` | mg/L | Naturally occurring dissolved mineral |
| `Conductivity` | µS/cm | Electrical conductivity (proxy for dissolved ions) |
| `Organic_carbon` | ppm | Total organic carbon from decayed matter |
| `Trihalomethanes` | µg/L | By-products of chlorination |
| `Turbidity` | NTU | Cloudiness; WHO guideline < 1 NTU for drinking water |

---

## Preprocessing workflow

The preprocessing pipeline is deliberately minimal. Its only job is to produce
clean, correctly-split files. All stateful transformations (imputation, scaling)
are deferred to the training pipeline so they are **fitted exclusively on training
data**, preventing data leakage.

```
dataset/raw/water_potability.csv   (never modified)
              │
              ▼
  ml/scripts/preprocess.py
    1. Remove exact duplicate rows
    2. Report missing values (not filled here)
    3. Stratified 80/20 train/test split  (random_seed=42, stratify=Potability)
              │
    ┌─────────┴──────────┐
    ▼                    ▼
train.csv            test.csv          ← locked; not used until final evaluation
(≈ 2,620 rows)       (≈ 656 rows)
```

### Preprocessing decisions

| Step | Decision | Reason |
|---|---|---|
| Duplicate removal | Remove | Identical samples add no information |
| Missing-value imputation | **Not here** — inside Pipeline in `train.py` | Prevents data leakage: imputer stats fitted on training data only |
| Outlier capping | Disabled | EDA skewness near-zero for all features; tree models are robust |
| Feature scaling | **Not here** — inside Pipeline in `train.py` | Same leakage reason; scaler fitted on training data only |
| Class imbalance | `class_weight='balanced'` in classifier | Simplest correct approach; no SMOTE at this stage |
| Train/test split | Stratified 80/20 | Preserves class ratio in both halves; reproducible via fixed seed |

---

## Training workflow (Phase 2)

Each candidate model is wrapped in a scikit-learn `Pipeline` that includes all
stateful preprocessing steps. The pipeline is fitted on training data only and
applied consistently to test data.

```
train.csv
    │
    ▼
Pipeline A — Logistic Regression
  SimpleImputer(strategy="median")
  → StandardScaler()
  → LogisticRegression(class_weight="balanced", max_iter=1000)

Pipeline B — Random Forest
  SimpleImputer(strategy="median")
  → RandomForestClassifier(n_estimators=300, class_weight="balanced")
```

### Model selection via cross-validation

- Stratified 5-fold cross-validation on the training set.
- Metrics reported per fold: accuracy, precision, recall, F1-score, ROC-AUC.
- Best pipeline selected based on mean cross-validation F1 and ROC-AUC.
- The held-out test set (`test.csv`) is **not used during model selection**.

### Final evaluation

After model selection, the best pipeline is re-fitted on the full training set
and evaluated **once** on `test.csv`. Reported metrics:

| Metric | Reason |
|---|---|
| Accuracy | Broad correctness |
| Precision | Avoid false "safe" labels |
| Recall | Catch all unsafe water |
| F1-score | Balance of precision/recall |
| Confusion matrix | Visualise error types |
| ROC-AUC | Threshold-independent performance |

Results saved to `ml/reports/evaluation.json`.

---

## Model artefact

The saved `.joblib` file is a complete scikit-learn Pipeline object:

```
ml/models/water_quality_model.joblib
  └─ Pipeline
       ├─ SimpleImputer      ← fitted on training data (median fill values stored)
       ├─ StandardScaler     ← fitted on training data (mean/std stored) [LR only]
       └─ Classifier         ← fitted model weights
```

The backend loads this single file and calls `pipeline.predict([[...]])` directly.
Imputation and scaling are applied automatically in the correct order.

---

## Explainability (Phase 6)

SHAP (SHapley Additive exPlanations) will be used to generate per-prediction
feature importance scores that are returned to the frontend alongside the
potability verdict.

---

## Artefacts

| File | Description |
|---|---|
| `dataset/raw/water_potability.csv` | Original dataset — never modified |
| `dataset/processed/train.csv` | Training split (80 %, stratified) |
| `dataset/processed/test.csv` | Held-out test split (20 %, stratified) |
| `ml/reports/eda_report.json` | EDA summary statistics |
| `ml/reports/preprocessing_report.json` | Split row counts, class distributions, missing-value counts |
| `ml/models/water_quality_model.joblib` | Serialised scikit-learn Pipeline (after Phase 2) |
| `ml/reports/evaluation.json` | Test-set metrics (after Phase 2) |
| `ml/reports/feature_importance.png` | Global feature importance bar chart (after Phase 6) |
