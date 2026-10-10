"""
Prediction router -- POST /api/predict

Accepts nine water-quality features, runs them through the trained
scikit-learn Pipeline, and returns the potability prediction with
probability scores and a mandatory disclaimer.

The pipeline (SimpleImputer -> RandomForestClassifier) was trained on
dataset/processed/train.csv and saved to ml/models/water_quality_model.joblib
during Phase 2.  It is loaded once at application startup via the lifespan
handler in main.py and retrieved here via get_model().
"""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.models.prediction import (
    FIELD_TO_TRAINING_COLUMN,
    PredictionResponse,
    WaterSample,
)
from app.services.model_loader import get_model

router = APIRouter()

_DISCLAIMER = (
    "AquaPura provides preliminary screening only. "
    "Class 1 ('potable') is the label used in the original research dataset "
    "and does NOT constitute certified drinking-water safety testing. "
    "Always defer to accredited laboratory analysis before making "
    "drinking-water safety decisions."
)


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict water potability",
    description=(
        "Submit nine water-quality measurements. "
        "Returns the model's potability prediction (class 0 = not-potable label, "
        "class 1 = potable label), probability scores, and a mandatory disclaimer. "
        "This is a preliminary screening tool only."
    ),
)
def predict_potability(sample: WaterSample) -> PredictionResponse:
    """
    Run the trained ML pipeline on the submitted water sample.

    Steps
    -----
    1. Validate and parse the request body (done by Pydantic before this runs).
    2. Build a single-row DataFrame with the exact column names the pipeline
       was trained on (mixed-case, matching the original dataset headers).
    3. Call pipeline.predict() for the class label.
    4. Call pipeline.predict_proba() for probability scores.
    5. Return a PredictionResponse with the disclaimer.

    Raises
    ------
    HTTPException 503  -- model artifact was not loaded at startup.
    HTTPException 500  -- unexpected error during inference.
    """
    # Step 1: retrieve the loaded pipeline (raises 503 if not loaded)
    try:
        pipeline = get_model()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Model not available: {exc}",
        ) from exc

    # Step 2: map JSON field names to training column names and build DataFrame.
    # The pipeline's SimpleImputer recorded feature_names_in_ during fit, so
    # the column order must match training.  FIELD_TO_TRAINING_COLUMN preserves
    # that order because it was defined in the same order as FEATURE_COLUMNS.
    row = {
        training_col: getattr(sample, json_field)
        for json_field, training_col in FIELD_TO_TRAINING_COLUMN.items()
    }
    input_df = pd.DataFrame([row])

    # Step 3 & 4: inference
    try:
        label = int(pipeline.predict(input_df)[0])

        prob_not_potable: float | None = None
        prob_potable: float | None = None
        if hasattr(pipeline, "predict_proba"):
            probs = pipeline.predict_proba(input_df)[0]
            # pipeline.classes_ is [0, 1] for this binary classifier
            prob_not_potable = round(float(probs[0]), 6)
            prob_potable     = round(float(probs[1]), 6)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inference error: {exc}",
        ) from exc

    return PredictionResponse(
        potable_label=label,
        potable=(label == 1),
        probability_potable=prob_potable,
        probability_not_potable=prob_not_potable,
        disclaimer=_DISCLAIMER,
    )
