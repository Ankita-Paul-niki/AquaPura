"""
Users router — protected endpoints for the authenticated user.

GET  /api/users/me                — return current user profile
GET  /api/users/me/analyses       — list all analyses for the current user
POST /api/users/me/analyses       — save a new analysis record
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.base import get_db
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the authenticated user."""
    return current_user


@router.get("/me/analyses", response_model=list[AnalysisResponse])
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all analyses belonging to the authenticated user, newest first."""
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.timestamp.desc())
        .all()
    )


@router.post(
    "/me/analyses",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_analysis(
    body: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist a new analysis record for the authenticated user."""
    analysis = Analysis(user_id=current_user.id, **body.model_dump())
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
