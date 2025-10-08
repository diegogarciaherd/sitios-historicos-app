from src.core.database import Base
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class EstadoConservacion(enum.Enum):
    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"

class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

class SitioHistorico(Base):
    __tablename__ = 'sitios_historicos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcionBreve: Mapped[str] = mapped_column(Text, nullable=False)
    descripcionCompleta: Mapped[str] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[EstadoConservacion] = mapped_column(Enum(EstadoConservacion), nullable=False)
    añoInauguracion: Mapped[int] = mapped_column(Integer, nullable=True)
    categoria_id: Mapped[int] = mapped_column(Integer, ForeignKey("categorias.id"), nullable=False)
    categoria: Mapped[Categoria] = relationship("Categoria", backref="sitios_historicos")
    fechaRegistro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)