# admin/src/core/models/site_history.py

from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime   # 👈 AGREGÁ ESTA LÍNEA

from core.database import Base, db
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Solo para type hints, no en runtime
if TYPE_CHECKING:
    from core.models.favorites import Favorite


# ---------------------------------------------
# Modelo de historial de cambios de sitios
# ---------------------------------------------


class SiteChange(Base):
    """Registro de un cambio sobre un sitio histórico.

    Cada fila representa una modificación de algún campo del sitio.
    """

    __tablename__ = "sites_history"

    # (acá mantené exactamente lo que ya tenías:
    # id, site_id, user_id, action, field, old_value, new_value, etc.)
    ...

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Relación con favoritos (no genera FK extra, solo ORM)
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="site",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Representación legible del cambio, útil para debug y logs."""
        return f"<SiteChange {self.action} site={self.site_id} field={self.field}>"
