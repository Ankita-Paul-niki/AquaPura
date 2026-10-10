"""
Pydantic schemas for water-quality prediction requests and responses.

Field-name note
---------------
The JSON request body uses lowercase field names (e.g. "hardness") because
that is the most natural convention for an HTTP API.  Internally the router
maps these to the exact column names the trained scikit-learn pipeline expects
(e.g. "Hardness"), which match the original dataset header casing.

The mapping is defined in FIELD_MAP at the bottom of this module and is the
single source of truth -- change it here if the training columns ever change.
"""

from __future__ import annotations

import math

from pydantic import BaseModel, Field, field_validator


class WaterSample(BaseModel):
    """
    Input features for a single water-potability prediction request.

    All nine features are required.  Omitting any field, or supplying a
    non-numeric, NaN, or infinite value, returns a 422 Unprocessable Entity
    error with a description of which field failed and why.

    These ranges are informational only and are not regulatory thresholds.
    Submitting a value outside a typical range does not certify safety or
    danger; the model was trained on a compiled research dataset, not live
    field measurements.
    """

    ph: float = Field(
        ...,
        ge=0.0,
        le=14.0,
        description="pH of the water sample (0-14 scale).",
    )
    hardness: float = Field(
        ...,
        gt=0.0,
        description="Hardness in mg/L (calcium and magnesium salts).",
    )
    solids: float = Field(
        ...,
        gt=0.0,
        description="Total dissolved solids in ppm.",
    )
    chloramines: float = Field(
        ...,
        ge=0.0,
        description="Chloramines concentration in ppm.",
    )
    sulfate: float = Field(
        ...,
        ge=0.0,
        description="Sulfate concentration in mg/L.",
    )
    conductivity: float = Field(
        ...,
        gt=0.0,
        description="Electrical conductivity in uS/cm.",
    )
    organic_carbon: float = Field(
        ...,
        ge=0.0,
        description="Total organic carbon in ppm.",
    )
    trihalomethanes: float = Field(
        ...,
        ge=0.0,
        description="Trihalomethanes concentration in ug/L.",
    )
    turbidity: float = Field(
        ...,
        ge=0.0,
        description="Turbidity in NTU.",
    )

    @field_validator(
        "ph", "hardness", "solids", "chloramines", "sulfate",
        "conductivity", "organic_carbon", "trihalomethanes", "turbidity",
        mode="before",
    )
    @classmethod
    def reject_non_finite(cls, v: object) -> object:
        """Reject NaN and ±infinity before Pydantic's range checks run."""
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("Value must be a finite number (not NaN or infinity).")
        return v


# ── Mapping: JSON field name  →  training column name ─────────────────────────
# The pipeline's SimpleImputer stored feature_names_in_ from the training CSV,
# which uses mixed-case headers matching the original Kaggle dataset.
FIELD_TO_TRAINING_COLUMN: dict[str, str] = {
    "ph":               "ph",
    "hardness":         "Hardness",
    "solids":           "Solids",
    "chloramines":      "Chloramines",
    "sulfate":          "Sulfate",
    "conductivity":     "Conductivity",
    "organic_carbon":   "Organic_carbon",
    "trihalomethanes":  "Trihalomethanes",
    "turbidity":        "Turbidity",
}


# ── Response schemas ───────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """
    Response returned by POST /api/predict.

    Fields
    ------
    potable_label : int
        Raw model output.  0 = the dataset's "not potable" class.
                           1 = the dataset's "potable" class.
        This is the label assigned in the original Kaggle research dataset and
        does NOT constitute certified drinking-water safety testing.

    potable : bool
        Convenience boolean.  True when potable_label == 1.

    probability_potable : float | None
        Probability assigned to class 1 by the Random Forest classifier
        (range 0.0 -- 1.0).  Present when the model supports predict_proba.
        A high value means the model leans toward the dataset's potable label;
        it is NOT a guarantee the water is safe to drink.

    probability_not_potable : float | None
        Probability assigned to class 0.

    disclaimer : str
        Mandatory disclaimer included in every response.
    """

    potable_label: int = Field(
        ...,
        description="Model class output: 0 = not-potable label, 1 = potable label.",
    )
    potable: bool = Field(
        ...,
        description="True if potable_label == 1 (dataset potable class).",
    )
    probability_potable: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "Probability of the potable-label class (0.0-1.0). "
            "Not a guarantee of safety."
        ),
    )
    probability_not_potable: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Probability of the not-potable-label class (0.0-1.0).",
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory screening disclaimer.",
    )
