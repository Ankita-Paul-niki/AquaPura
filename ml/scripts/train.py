"""
AquaPura -- Phase 2: Model Training
=====================================

What this script does
---------------------
1. Loads the pre-split training data from dataset/processed/train.csv.
   The held-out test set (test.csv) is NOT touched until final evaluation.

2. Builds two scikit-learn Pipelines:

   Pipeline A -- Logistic Regression
     Step 1: SimpleImputer(strategy="median")  -- fills NaNs using training medians
     Step 2: StandardScaler()                  -- centres/scales features (required for LR)
     Step 3: LogisticRegression(class_weight="balanced")

   Pipeline B -- Random Forest
     Step 1: SimpleImputer(strategy="median")  -- fills NaNs using training medians
     Step 2: RandomForestClassifier(class_weight="balanced")
     (Tree models do not require scaling.)

   Why "balanced" class_weight?
   The dataset has ~61% non-potable vs ~39% potable. Without adjustment a naive
   model just predicts "not potable" most of the time and looks deceptively
   accurate. Setting class_weight="balanced" tells scikit-learn to penalise
   mistakes on the minority class more heavily, so the model actually tries to
   identify potable water correctly.

3. Runs stratified 5-fold cross-validation on the training set for each pipeline.
   Reports mean +/- std for: accuracy, precision, recall, F1-score, ROC-AUC.

   Why F1 and ROC-AUC for model selection?
   - Accuracy alone is misleading on imbalanced data (61/39 split).
   - F1 balances precision (how often a "potable" prediction is correct) and
     recall (how many genuinely potable samples we caught).
   - ROC-AUC measures discrimination quality across all decision thresholds.
   Together they give a fuller picture. The model with higher mean F1 and
   ROC-AUC on the cross-validation folds is selected.

4. Re-fits the selected pipeline on the FULL training set.

5. Evaluates ONCE on the held-out test set (test.csv).
   Reported metrics: accuracy, precision, recall, F1-score, ROC-AUC,
   confusion matrix.
   Results saved to ml/reports/evaluation.json.

6. Saves the fitted pipeline to ml/models/water_quality_model.joblib.
   This single file contains the imputer + optional scaler + classifier,
   ready for the FastAPI backend to call pipeline.predict() directly.

DISCLAIMER
----------
Class 1 in this dataset is labelled "potable" by the original data compiler.
This does NOT mean the water is certified safe to drink. AquaPura is a
preliminary screening tool only and must not be used as the sole basis for
drinking-water safety decisions. Always defer to accredited laboratory analysis.

HOW TO RUN
----------
    python ml/scripts/train.py

Prerequisites: pandas, scikit-learn, joblib (all installed in venv).
Run AFTER ml/scripts/preprocess.py.
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parents[2]
TRAIN_CSV  = ROOT / "dataset" / "processed" / "train.csv"
TEST_CSV   = ROOT / "dataset" / "processed" / "test.csv"
MODEL_PATH = ROOT / "ml" / "models" / "water_quality_model.joblib"
REPORTS    = ROOT / "ml" / "reports"

# ── Settings ───────────────────────────────────────────────────────────────────
TARGET      = "Potability"
RANDOM_SEED = 42
CV_FOLDS    = 5


def build_pipelines():
    """Return the two candidate pipelines."""

    # Pipeline A: Logistic Regression
    # SimpleImputer fills missing values with the column median (computed on
    # training data only -- no leakage). StandardScaler then centres and scales
    # each feature to mean=0, std=1, which Logistic Regression requires to
    # converge reliably. class_weight="balanced" compensates for the 61/39 split.
    pipe_lr = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf",     LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=RANDOM_SEED,
        )),
    ])

    # Pipeline B: Random Forest
    # Same median imputer. No scaler needed -- decision trees split on feature
    # values directly and are not affected by scale. n_estimators=300 means the
    # forest grows 300 trees and averages their votes. n_jobs=-1 uses all CPU
    # cores to speed up training.
    pipe_rf = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("clf",     RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )),
    ])

    return {"LogisticRegression": pipe_lr, "RandomForest": pipe_rf}


def run_cross_validation(pipelines, X_train, y_train):
    """
    Run stratified 5-fold CV for each pipeline.
    Returns a dict of {model_name: {metric: {"mean": ..., "std": ...}}}.
    """
    cv      = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True,
                               random_state=RANDOM_SEED)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    cv_results = {}

    for name, pipe in pipelines.items():
        print(f"\n  Running {CV_FOLDS}-fold CV for {name} ...")
        raw = cross_validate(pipe, X_train, y_train, cv=cv,
                             scoring=scoring, n_jobs=-1)
        cv_results[name] = {}
        for metric in scoring:
            scores = raw[f"test_{metric}"]
            cv_results[name][metric] = {
                "mean": round(float(scores.mean()), 6),
                "std":  round(float(scores.std()),  6),
            }
        print(f"  {name} results:")
        for metric, vals in cv_results[name].items():
            print(f"    {metric:<12s}: {vals['mean']:.4f}  +/- {vals['std']:.4f}")

    return cv_results


def select_best(cv_results, pipelines):
    """
    Pick the pipeline with the highest mean F1 on the CV folds.
    In case of a tie (within 0.001), prefer the model with higher ROC-AUC.
    Returns (best_name, best_pipeline).
    """
    best_name = max(
        cv_results,
        key=lambda n: (
            cv_results[n]["f1"]["mean"],
            cv_results[n]["roc_auc"]["mean"],
        ),
    )
    return best_name, pipelines[best_name]


def evaluate_on_test(pipeline, X_test, y_test):
    """
    Evaluate a fitted pipeline on the held-out test set.
    Returns a dict of metrics suitable for JSON serialisation.
    """
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    cm     = confusion_matrix(y_test, y_pred).tolist()
    auc    = float(roc_auc_score(y_test, y_prob))

    return {
        "classification_report": report,
        "confusion_matrix":      cm,
        "roc_auc":               round(auc, 6),
    }


def main():
    print("\n" + "=" * 60)
    print("  AquaPura -- Model Training  (Phase 2)")
    print("=" * 60)

    # ── Guard: splits must exist ───────────────────────────────────────────────
    for path in (TRAIN_CSV, TEST_CSV):
        if not path.exists():
            print(f"\n[ERROR] Required file not found: {path}")
            print("  Run ml/scripts/preprocess.py first.")
            sys.exit(1)

    # ── 1. Load training data ─────────────────────────────────────────────────
    print("\n[1] Loading training data ...")
    train_df = pd.read_csv(TRAIN_CSV)
    X_train  = train_df.drop(columns=[TARGET])
    y_train  = train_df[TARGET]
    print(f"    {len(train_df):,} rows  |  features: {list(X_train.columns)}")
    print(f"    Class distribution -- 0: {(y_train==0).sum()}  "
          f"1: {(y_train==1).sum()}")

    # ── 2. Build pipelines ────────────────────────────────────────────────────
    print("\n[2] Building pipelines ...")
    pipelines = build_pipelines()
    for name in pipelines:
        print(f"    {name}: OK")

    # ── 3. Cross-validation on training set ───────────────────────────────────
    print("\n[3] Cross-validation on training set "
          f"(StratifiedKFold, {CV_FOLDS} folds, seed={RANDOM_SEED}) ...")
    cv_results = run_cross_validation(pipelines, X_train, y_train)

    # ── 4. Select best model ──────────────────────────────────────────────────
    best_name, best_pipe = select_best(cv_results, pipelines)
    print(f"\n[4] Selected model: {best_name}")
    print(f"    Selection criterion: highest mean F1 on CV folds "
          f"(tie-break: ROC-AUC)")
    print(f"    CV F1    = {cv_results[best_name]['f1']['mean']:.4f}")
    print(f"    CV AUC   = {cv_results[best_name]['roc_auc']['mean']:.4f}")

    # ── 5. Re-fit on full training set ────────────────────────────────────────
    print(f"\n[5] Refitting {best_name} on full training set "
          f"({len(train_df):,} rows) ...")
    best_pipe.fit(X_train, y_train)
    print("    Done.")

    # ── 6. Evaluate on held-out test set (ONCE) ───────────────────────────────
    print("\n[6] Evaluating on held-out test set ...")
    test_df = pd.read_csv(TEST_CSV)
    X_test  = test_df.drop(columns=[TARGET])
    y_test  = test_df[TARGET]
    print(f"    {len(test_df):,} rows  |  "
          f"Class 0: {(y_test==0).sum()}  Class 1: {(y_test==1).sum()}")

    test_metrics = evaluate_on_test(best_pipe, X_test, y_test)

    print("\n    --- Test-set classification report ---")
    print(classification_report(
        y_test, best_pipe.predict(X_test),
        target_names=["Class 0 (not potable)", "Class 1 (potable label)"],
    ))
    print(f"    ROC-AUC : {test_metrics['roc_auc']:.4f}")
    cm = test_metrics["confusion_matrix"]
    print(f"    Confusion matrix (rows=actual, cols=predicted):")
    print(f"      [TN={cm[0][0]:3d}  FP={cm[0][1]:3d}]")
    print(f"      [FN={cm[1][0]:3d}  TP={cm[1][1]:3d}]")

    # ── 7. Save evaluation report ─────────────────────────────────────────────
    REPORTS.mkdir(parents=True, exist_ok=True)
    evaluation = {
        "disclaimer": (
            "Class 1 ('potable') is the label used in the original Kaggle "
            "dataset and does NOT constitute certification of drinking-water "
            "safety. AquaPura is a preliminary screening tool only."
        ),
        "model_selection": {
            "criterion": "highest mean F1 on 5-fold stratified CV (tie-break: ROC-AUC)",
            "selected_model": best_name,
            "cv_results": cv_results,
        },
        "test_set_evaluation": {
            "n_samples":    len(test_df),
            "class_counts": {"0": int((y_test==0).sum()),
                             "1": int((y_test==1).sum())},
            **test_metrics,
        },
        "model_artifact": str(MODEL_PATH.relative_to(ROOT)),
        "random_seed":     RANDOM_SEED,
        "cv_folds":        CV_FOLDS,
    }
    eval_path = REPORTS / "evaluation.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2)
    print(f"\n[7] Saved evaluation report: {eval_path.relative_to(ROOT)}")

    # ── 8. Save model pipeline ────────────────────────────────────────────────
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipe, MODEL_PATH)
    print(f"[8] Saved model pipeline:    {MODEL_PATH.relative_to(ROOT)}")

    print("\n  Done. Phase 2 complete.")
    print("  Next step: Phase 3 -- API integration (backend/app)")
    print("=" * 60)


if __name__ == "__main__":
    main()
