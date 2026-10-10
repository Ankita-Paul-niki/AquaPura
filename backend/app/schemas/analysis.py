"""
Pydantic schemas for analysis endpoints.
"""

from datetime import datetime

from pydantic import BaseModel


class AnalysisCreate(BaseModel):
    ph:               float
    hardness:         float
    solids:           float
    chloramines:      float
    sulfate:          float
    conductivity:     float
    organic_carbon:   float
    trihalomethanes:  float
    turbidity:        float
    potable_label:       int
    probability_potable: float | None = None


class AnalysisResponse(AnalysisCreate):
    id:        int
    user_id:   int
    timestamp: datetime

    model_config = {"from_attributes": True}
