# admin/src/core/models/sites.py
from core.database import Base, db
import enum
from datetime import datetime

from sqlalchemy import (
    String, Text, Float, Integer, DateTime, Boolean, Enum,
    ForeignKey, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from core.models.tags import Tag

# --------------------------------------------------------------------
# Tabla de asociación Site <-> Tag
# --------------------------------------------------------------------
sites_tags = Table(
    "sites_tags",
    Base.metadata,
    Column("site_id", Integer, ForeignKey("sitios_historicos.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

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

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=sites_tags,
        backref="sitios_historicos",
        lazy="select",
    )

    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    localizacion: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # ------ helpers geométricos
    @property
    def lat(self) -> float | None:
        if self.localizacion:
            p = to_shape(self.localizacion)
            return p.y
        return None

    @property
    def lng(self) -> float | None:
        if self.localizacion:
            p = to_shape(self.localizacion)
            return p.x
        return None

    def to_dict(self) -> dict:
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

# --------------------------------------------------------------------
# Queries básicas
# --------------------------------------------------------------------
def list_sites(page=1, per_page=10):
    q = db.session.query(SitioHistorico)
    total = q.count()
    sites = q.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total

def list_sites_with_filters(filters, page=1, per_page=10):
    q = db.session.query(SitioHistorico)
    q = apply_filters(q, filters)
    total = q.count()
    data = q.offset((page - 1) * per_page).limit(per_page).all()
    return data, total

def get_all_provinces():
    return db.session.query(SitioHistorico.provincia).distinct().all()

def get_all_cities():
    return db.session.query(SitioHistorico.ciudad).distinct().all()

def get_site(id: int):
    return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first()

# --------------------------------------------------------------------
# Crear / actualizar / eliminar
# --------------------------------------------------------------------
def create_sites(**kwargs):
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    año = kwargs.get("añoInauguracion")
    if año:
        kwargs["añoInauguracion"] = int(año)

    site = SitioHistorico(**kwargs)

    if lat is not None and lng is not None:
        site.localizacion = WKTElement(f"POINT({float(lng)} {float(lat)})", srid=4326)

    db.session.add(site)
    db.session.commit()
    return site

def update_site(id: int, **kwargs):
    site = get_site(id)
    if not site:
        raise ValueError(f"Sitio con id {id} no encontrado")

    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    año = kwargs.get("añoInauguracion")
    if año is not None:
        if año == "":
            kwargs["añoInauguracion"] = None
        else:
            try:
                kwargs["añoInauguracion"] = int(año)
            except (ValueError, TypeError):
                raise ValueError("El año de inauguración debe ser un número válido")

    for k, v in kwargs.items():
        if hasattr(site, k):
            setattr(site, k, v)

    if lat is not None and lng is not None:
        try:
            site.localizacion = WKTElement(f"POINT({float(lng)} {float(lat)})", srid=4326)
        except (ValueError, TypeError):
            raise ValueError("Las coordenadas deben ser números válidos")

    db.session.commit()
    return site

def delete_site(id: int):
    site = get_site(id)
    if site:
        db.session.delete(site)
        db.session.commit()
    return site

# --------------------------------------------------------------------
# Filtros
# --------------------------------------------------------------------
def apply_filters(query, filters):
    if not filters:
        return query

    if filters.get("search"):
        term = f"%{filters['search']}%"
        query = query.filter(
            (SitioHistorico.nombre.ilike(term)) |
            (SitioHistorico.descripcionBreve.ilike(term))
        )

    if filters.get("city"):
        query = query.filter(SitioHistorico.ciudad.ilike(filters["city"]))

    if filters.get("province"):
        query = query.filter(SitioHistorico.provincia.ilike(filters["province"]))

    if filters.get("status"):
        try:
            estado_enum = EstadoConservacion[filters["status"].upper()]
            query = query.filter(SitioHistorico.estado == estado_enum)
        except KeyError:
            pass

    visibility = True if "visibility" not in filters else (str(filters["visibility"]).lower() == "true")
    query = query.filter(SitioHistorico.visible == visibility)

    if filters.get("startDate"):
        try:
            start_date = datetime.strptime(filters["startDate"], "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro >= start_date)
        except ValueError:
            pass

    if filters.get("endDate"):
        try:
            end_date = datetime.strptime(filters["endDate"], "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro <= end_date)
        except ValueError:
            pass

    return query

# --------------------------------------------------------------------
# Export CSV (usa COPY de PostgreSQL)
# --------------------------------------------------------------------
def export_to_csv(file_path: str, filters: dict | None = None):
    q = db.session.query(
        SitioHistorico.id,
        SitioHistorico.nombre,
        SitioHistorico.descripcionBreve,
        SitioHistorico.ciudad,
        SitioHistorico.provincia,
        SitioHistorico.estado,
        SitioHistorico.fechaRegistro,
        SitioHistorico.localizacion,
    )
    q = apply_filters(q, filters)

    if q.count() == 0:
        raise ValueError("No hay datos para exportar con los filtros proporcionados.")

    compiled = q.statement.compile(
        dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
    )

    with open(file_path, "w", encoding="utf-8") as csvfile:
        conn = db.session.connection().connection
        cur = conn.cursor()
        try:
            sql = f"COPY ({str(compiled)}) TO STDOUT WITH CSV HEADER"
            cur.copy_expert(sql, csvfile)
        finally:
            cur.close()
