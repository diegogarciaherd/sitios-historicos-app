from core.database import Base, db
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

class EstadoConservacion(enum.Enum):
    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"


class SitioHistorico(Base):
    __tablename__ = "sitios_historicos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcionBreve: Mapped[str] = mapped_column(Text, nullable=True)
    descripcionCompleta: Mapped[str] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=True)
    provincia: Mapped[str] = mapped_column(String(100), nullable=True)
    estado: Mapped[EstadoConservacion] = mapped_column(
        Enum(EstadoConservacion, native_enum=False, validate_strings=True),
        nullable=False,
    )
    añoInauguracion: Mapped[int] = mapped_column(Integer, nullable=True)
    categoria: Mapped[str] = mapped_column(Text, nullable=True)
    fechaRegistro: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    localizacion: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    @property 
    def lat(self) -> float:
        "Devuelve la latitud del sitio"
        if self.localizacion: 
            punto = to_shape(self.localizacion)
            return punto.y # Latitud
        return None

    @property
    def lng(self) -> float:
        "Devuelve la longitud del sitio"
        if self.localizacion: 
            punto = to_shape(self.localizacion)
            return punto.x # Longitud
        return None
    
    def to_dict(self) -> dict:
        """Convierte el sitio a un diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcionBreve": self.descripcionBreve,
            "descripcionCompleta": self.descripcionCompleta,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "estado": self.estado.value if isinstance(self.estado, enum.Enum) else self.estado,
            "añoInauguracion": self.añoInauguracion,
            "categoria": self.categoria,
            "lat": self.lat,
            "lng": self.lng,
            "fechaRegistro": self.fechaRegistro.isoformat() if self.fechaRegistro else None,
            "visible": self.visible,
        }

def list_sites(page=1, per_page=10):
    query = db.session.query(SitioHistorico)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites , total


def create_sites(**kwargs):
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    site = SitioHistorico(**kwargs)

    if lat is not None and lng is not None:
        site.localizacion = WKTElement(f'POINT({lng} {lat})', srid=4326)

    db.session.add(site)
    db.session.commit()
    return site  

def update_site(id, **kwargs):
    site = get_site(id)
    for key, value in kwargs.items():
        setattr(site, key, value)
    lat = site.lat
    lng = site.lng
    site.localizacion = WKTElement(f'POINT({lng} {lat})', srid=4326)
    db.session.commit()
    return site


def get_site(id):
    return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first()


def delete_site(id):
    site = get_site(id)
    db.session.delete(site)
    db.session.commit()
    return site
