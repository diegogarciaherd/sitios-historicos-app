# admin/src/core/models/site_history.py
"""
Modelo SiteChange: historial de cambios de un sitio histórico.

Cada fila representa una modificación de un campo del sitio,
incluyendo quién realizó el cambio y cuándo.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    # Solo para anotaciones de tipo, sin imports circulares
    from core.models.sites import SitioHistorico
    from core.models.user import User


class SiteChange(Base):
    __tablename__ = "sites_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ----------------------
    # FK al sitio histórico
    # ----------------------
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"),
        nullable=False,
        index=True
    )

    # ----------------------
    # Usuario que hizo el cambio
    # ----------------------
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    # ----------------------
    # Tipo de acción
    # ----------------------
    action: Mapped[str] = mapped_column(
        Enum("create", "update", "delete", name="site_action"),
        nullable=False
    )

    # ----------------------
    # Campo editado
    # ----------------------
    field: Mapped[str | None] = mapped_column(String(64))

    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)

    # ----------------------
    # Fecha del cambio
    # ----------------------
    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # ----------------------
    # Relaciones (opcionales)
    # ----------------------
    site: Mapped["SitioHistorico"] = relationship("SitioHistorico")
    user: Mapped["User"] = relationship("User")



    def __repr__(self):
        return f"<SiteChange id={self.id} site={self.site_id} action={self.action}>"
