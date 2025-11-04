# admin/src/core/models/site_history.py
from core.database import Base, db
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

#Creamos una tabla sites_history con un registro por cambio de campo. Guarda: sitio, usuario, acción, campo, valor anterior/nuevo y timestamp.

class SiteChange(Base):
    __tablename__ = "sites_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sitios_historicos.id"), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(Enum("create", "update", "delete", name="site_action"), nullable=False)
    field: Mapped[str | None] = mapped_column(String(64))         # Null cuando sea create/delete “global”
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SiteChange {self.action} site={self.site_id} field={self.field}>"
