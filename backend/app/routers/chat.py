"""
Chat router -- POST /api/chat

Accepts a user message (and an optional prediction context) and returns
a reply from the AquaPura AI Assistant.

The assistant is currently implemented as a rule-based knowledge engine
(see app/services/knowledge_base.py).  To upgrade to a real LLM, replace
the `get_reply` call with an LLM API call -- the router itself does not change.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.knowledge_base import (
    PredictionContext as KBContext,
    get_reply,
)

router = APIRouter()

_DISCLAIMER = (
    "AquaPura AI Assistant provides educational guidance only. "
    "Responses do not constitute certified water-quality testing or health advice. "
    "Always defer to accredited laboratory analysis for drinking-water safety decisions."
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AquaPura AI Assistant",
    description=(
        "Send a message to the AquaPura AI Assistant. "
        "Optionally include the user's latest prediction result so the "
        "assistant can give context-aware replies. "
        "Returns an educational response and a mandatory disclaimer."
    ),
)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Route a user message to the knowledge-base engine and return a reply.

    Raises
    ------
    HTTPException 422  -- Pydantic validation failure (blank message, etc.)
    HTTPException 500  -- Unexpected error in the knowledge engine.
    """
    # Convert Pydantic PredictionContext to the knowledge-base dataclass
    kb_context: KBContext | None = None
    if request.prediction_context is not None:
        pc = request.prediction_context
        kb_context = KBContext(
            potable=pc.potable,
            potable_label=pc.potable_label,
            probability_potable=pc.probability_potable,
            probability_not_potable=pc.probability_not_potable,
        )

    try:
        reply = get_reply(request.message, kb_context)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat engine error: {exc}",
        ) from exc

    return ChatResponse(reply=reply, disclaimer=_DISCLAIMER)
