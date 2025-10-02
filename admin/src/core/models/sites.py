from src.core.database import Base
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.core.database import db
from geoalchemy2 import Geometry

class EstadoConservacion(enum.Enum):
    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"


class SitioHistorico(Base):
    __tablename__ = 'sitios_historicos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcionBreve: Mapped[str] = mapped_column(Text, nullable=True)
    descripcionCompleta: Mapped[str] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[EstadoConservacion] = mapped_column(
        Enum(EstadoConservacion, native_enum=False, validate_strings=True),
        nullable=False
    )
    añoInauguracion: Mapped[int] = mapped_column(Integer, nullable=True)
    categoria: Mapped[str] = mapped_column(Text, nullable=True)
    fechaRegistro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    localizacion: Mapped[Geometry] = mapped_column(Geometry(geometry_type='POINT', srid=4326), nullable=False)

def list_sites(page=1, per_page=10):
    query = db.session.query(SitioHistorico)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total

def create_sites(**kwargs):
	site = SitioHistorico(**kwargs)
	db.session.add(site)
	db.session.commit()
	return site

def update_site(id, **kwargs):
	site = get_site(id)
	for key, value in kwargs.items():
		setattr(site, key, value)
	db.session.commit()
	return site 

def get_site(id):
	return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first() 

def delete_site(id):
	site = get_site(id)
	db.session.delete(site)
	db.session.commit()
	return site

