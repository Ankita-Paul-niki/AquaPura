"""
Pydantic schemas for the chat endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class PredictionContext(BaseModel):
    """
    Optional prediction result passed by the frontend so the chatbot can
    give context-aware replies (e.g. 'What does my result mean?').

    These fields mirror the PredictionResponse schema from prediction.py.
    All fields are optional so the frontend can omit them if no prediction
    has been made yet.
    """

    potable: bool = Field(..., description="True = potable label, False = not-potable label.")
    potable_label: int = Field(..., description="Raw class label: 0 or 1.")
    probability_potable: float | None = Field(None, ge=0.0, le=1.0)
    probability_not_potable: float | None = Field(None, ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    """Body of POST /api/chat."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User message text (1 – 1000 characters).",
    )
    prediction_context: PredictionContext | None = Field(
        None,
        description=(
            "The user's most recent prediction result. "
            "When provided, the assistant can answer questions about it."
        ),
    )

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message must not be blank or whitespace only.")
        return v.strip()


class ChatResponse(BaseModel):
    """Body returned by POST /api/chat."""

    reply: str = Field(
        ...,
        description="Assistant reply in plain text / Markdown.",
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory screening disclaimer included in every response.",
    )
