#admin/src/core/models/reviews.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

import enum
class ReviewStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    site_id: Mapped[int] = mapped_column(ForeignKey("sitios_historicos.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)  # opcional

    rating: Mapped[int] = mapped_column(Integer, nullable=False)        # 1..5
    title:  Mapped[str] = mapped_column(String(120), nullable=False)
    body:   Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Moderación
    moderated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relaciones (opcionales para backrefs)
    site = relationship("SitioHistorico", back_populates="reviews", lazy="joined", innerjoin=True)
