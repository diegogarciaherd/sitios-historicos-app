# admin/src/core/models/site_history.py

from core.database import Base, db
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column


# ---------------------------------------------
# Modelo de historial de cambios de sitios
# ---------------------------------------------
# Acá no se guarda el sitio en sí, sino cada cambio puntual:
# - qué sitio fue
# - quién lo tocó
# - qué acción hizo (create / update / delete)
# - qué campo cambió
# - valor anterior y nuevo
# - y el timestamp del cambio
#
# Esto después sirve para auditar quién hizo qué en el admin.


class SiteChange(Base):
    """Registro de un cambio sobre un sitio histórico.

    Cada fila representa UNA modificación atómica: un campo, una acción,
    una fecha y, opcionalmente, el usuario que hizo el cambio.

    No tiene relación con favoritos porque los favoritos son del usuario
    sobre el sitio, no del cambio puntual.
    """

    __tablename__ = "sites_history"

    # PK del registro de cambio
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # FK al sitio histórico afectado
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"),
        index=True,
        nullable=False,
    )

    # Usuario que hizo el cambio (puede ser None si viene de un proceso automático)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    # Tipo de acción hecha sobre el sitio
    action: Mapped[str] = mapped_column(
        Enum("create", "update", "delete", name="site_action"),
        nullable=False,
    )

    # Nombre del campo modificado (None cuando la acción es "create" o "delete" global)
    field: Mapped[str | None] = mapped_column(String(64))

    # Valor anterior del campo (si aplica)
    old_value: Mapped[str | None] = mapped_column(Text)

    # Valor nuevo del campo (si aplica)
    new_value: Mapped[str | None] = mapped_column(Text)

    # Momento en que se registró el cambio (lo llena la BD)
    changed_at: Mapped[str] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representación legible del cambio, útil para debug y logs."""
        return f"<SiteChange {self.action} site={self.site_id} field={self.field}>"
