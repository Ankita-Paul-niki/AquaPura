"""
SQLAlchemy Analysis ORM model.

Stores one prediction run per row, linked to a registered user.
"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id:                  Mapped[int]            = mapped_column(primary_key=True, index=True)
    user_id:             Mapped[int]            = mapped_column(ForeignKey("users.id"), index=True)
    timestamp:           Mapped[datetime]       = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Input parameters
    ph:               Mapped[float]  = mapped_column(Float)
    hardness:         Mapped[float]  = mapped_column(Float)
    solids:           Mapped[float]  = mapped_column(Float)
    chloramines:      Mapped[float]  = mapped_column(Float)
    sulfate:          Mapped[float]  = mapped_column(Float)
    conductivity:     Mapped[float]  = mapped_column(Float)
    organic_carbon:   Mapped[float]  = mapped_column(Float)
    trihalomethanes:  Mapped[float]  = mapped_column(Float)
    turbidity:        Mapped[float]  = mapped_column(Float)

    # Prediction outputs
    potable_label:       Mapped[int]            = mapped_column(Integer)
    probability_potable: Mapped[float | None]   = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="analyses")  # noqa: F821
