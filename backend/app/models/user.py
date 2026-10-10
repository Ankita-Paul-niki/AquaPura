"""
SQLAlchemy User ORM model.
"""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True, index=True)
    full_name:       Mapped[str]      = mapped_column(String(150))
    email:           Mapped[str]      = mapped_column(String(254), unique=True, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(255))
    created_at:      Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    analyses: Mapped[list["Analysis"]] = relationship(  # noqa: F821
        "Analysis", back_populates="user", cascade="all, delete-orphan"
    )
