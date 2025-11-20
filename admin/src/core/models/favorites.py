# admin/src/core/models/favorites.py
"""
Modelo Favorite: representa la relación de sitios favoritos de un usuario.

Cada fila indica que un usuario marcó un sitio como favorito.
Se evita duplicado mediante UniqueConstraint(user_id, site_id).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

# TYPE_CHECKING para evitar imports circulares en runtime
if TYPE_CHECKING:
    from core.models.user import User
    from core.models.sites import SitioHistorico


class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint("user_id", "site_id", name="uq_user_site_favorite"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    user: Mapped["User"] = relationship(
        "User",
        back_populates="favorites",
    )

    site: Mapped["SitioHistorico"] = relationship(
        "SitioHistorico",
        back_populates="favorites",
    )

    def __repr__(self):
        return f"<Favorite user={self.user_id} site={self.site_id}>"
