"""
AquaPura -- ML model loader service.

Responsibilities
----------------
- Resolve the model artifact path relative to the project root, not the
  current working directory, so the API can be launched from any directory.
- Load the scikit-learn Pipeline once at application startup.
- Expose a single module-level accessor `get_model()` that all other code uses.
- Raise a clear RuntimeError at startup if the artifact is missing or corrupt,
  rather than failing silently on the first prediction request.

The loaded pipeline contains:
    SimpleImputer(strategy="median")
    RandomForestClassifier(class_weight="balanced", ...)
trained on dataset/processed/train.csv.  It expects a pandas DataFrame
with these exact column names (same casing as training):
    ph, Hardness, Solids, Chloramines, Sulfate, Conductivity,
    Organic_carbon, Trihalomethanes, Turbidity

This module does NOT retrain the model.  It only loads the pre-trained artifact.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

# ── Path resolution ────────────────────────────────────────────────────────────
# backend/app/services/model_loader.py  →  ../../..  →  project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_MODEL_PATH   = _PROJECT_ROOT / "ml" / "models" / "water_quality_model.joblib"

# Module-level slot; filled once during startup.
_model: Any | None = None

# The exact feature order the pipeline was trained on.
# Must match the column names in dataset/processed/train.csv.
FEATURE_COLUMNS: list[str] = [
    "ph",
    "Hardness",
    "Solids",
    "Chloramines",
    "Sulfate",
    "Conductivity",
    "Organic_carbon",
    "Trihalomethanes",
    "Turbidity",
]


def load_model() -> None:
    """
    Load (or reload) the ML pipeline from disk into the module-level slot.

    Called once from the FastAPI lifespan handler at startup.
    Raises RuntimeError if the artifact is missing or cannot be deserialised.
    """
    global _model

    if not _MODEL_PATH.exists():
        raise RuntimeError(
            f"Model artifact not found at {_MODEL_PATH}. "
            "Run ml/scripts/train.py first to generate the artifact."
        )

    try:
        pipeline = joblib.load(_MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load model artifact from {_MODEL_PATH}: {exc}"
        ) from exc

    # Basic sanity check: the loaded object must be a fitted sklearn Pipeline.
    if not hasattr(pipeline, "predict"):
        raise RuntimeError(
            f"Loaded artifact does not look like a scikit-learn pipeline "
            f"(missing .predict). Check {_MODEL_PATH}."
        )

    _model = pipeline


def get_model() -> Any:
    """
    Return the loaded pipeline.  Raises RuntimeError if called before
    load_model() has succeeded (e.g. during startup failure).
    """
    if _model is None:
        raise RuntimeError(
            "Model has not been loaded. "
            "This usually means the startup lifespan handler failed."
        )
    return _model
