# admin/src/core/models/favorites.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint("user_id", "site_id", name="uq_user_site_favorite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relaciones
    user: Mapped["User"] = relationship(
        "User", back_populates="favorites"
    )
    site: Mapped["SitioHistorico"] = relationship(
        "SitioHistorico", back_populates="favorites"
    )
