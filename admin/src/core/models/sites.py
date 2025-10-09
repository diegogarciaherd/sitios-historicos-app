# admin/src/core/models/sites.py
from __future__ import annotations

from core.database import Base, db
import enum
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Float,
    Integer,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    Table,
    Column,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql


# --------------------------------------------------------------------
# Enums / constantes (si ya existen en tu proyecto, podés reutilizarlos)
# --------------------------------------------------------------------
class EstadoSitio(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    borrador = "borrador"


# --------------------------------------------------------------------
# Asociación many-to-many Sitios <-> Tags
# (si ya existe en tu proyecto, mantené el mismo nombre de tabla)
# --------------------------------------------------------------------
sites_tags = Table(
    "sites_tags",
    Base.metadata,
    Column("site_id", ForeignKey("sitios_historicos.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


# --------------------------------------------------------------------
# Modelos (si tus modelos ya existen, esta definición respeta el estilo
# "development": mapped_column/Mapped + relationship con backref)
# --------------------------------------------------------------------
class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class SitioHistorico(Base):
    __tablename__ = "sitios_historicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), index=True)
    descripcionBreve: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[EstadoSitio] = mapped_column(
        Enum(EstadoSitio, name="estado_sitio"), default=EstadoSitio.activo
    )
    fechaRegistro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Si usás Geometry de geoalchemy, reemplazá por tu tipo real:
    localizacion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # >>> Mantener backref como en TU rama (evitar back_populates) <<<
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary=sites_tags,
        backref="sitios_historicos",
        lazy="select",
    )


# --------------------------------------------------------------------
# Helpers de catálogos (si en tu proyecto están en otro módulo, podés
# borrarlos de acá y usar los originales).
# --------------------------------------------------------------------
def get_all_cities() -> list[tuple[str]]:
    # Reemplazá por tu SELECT real si existe tabla de ciudades.
    # Devuelve lista de tuplas para mantener compatibilidad con controller.
    res = db.session.execute(func.unnest([ "La Plata", "Mar del Plata", "Bahía Blanca" ]))
    return [(row[0],) for row in res]


def get_all_provinces() -> list[tuple[str]]:
    res = db.session.execute(func.unnest([ "Buenos Aires", "Chubut", "Córdoba" ]))
    return [(row[0],) for row in res]


# Si tu proyecto ya tiene estas funciones en core.models.tags, ignorá estas:
def get_all_tags() -> list[Tag]:
    return db.session.query(Tag).order_by(Tag.name.asc()).all()


# --------------------------------------------------------------------
# Filtros reutilizables
# --------------------------------------------------------------------
def apply_filters(query, filters: dict | None):
    if not filters:
        return query

    f = {k: v for k, v in filters.items() if v not in (None, "", [])}

    # Fechas (yyyy-mm-dd)
    start = f.get("startDate")
    end = f.get("endDate")
    if start and end:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d")
            ed = datetime.strptime(end, "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro.between(sd, ed))
        except ValueError:
            # El controller ya valida y devuelve 400; aquí no rompemos.
            pass

    # Estado
    estado = f.get("estado")
    if estado and estado in EstadoSitio.__members__:
        query = query.filter(SitioHistorico.estado == EstadoSitio[estado])

    # Búsqueda por nombre (ilike)
    qtext = f.get("q")
    if qtext:
        query = query.filter(SitioHistorico.nombre.ilike(f"%{qtext}%"))

    # Filtrado por tag (id o nombre)
    tag = f.get("tag")
    if tag:
        tag_sub = db.session.query(Tag.id).filter(
            (Tag.id == tag) | (Tag.name.ilike(f"%{tag}%"))
        )
        query = query.filter(SitioHistorico.tags.any(Tag.id.in_(tag_sub)))

    return query


# --------------------------------------------------------------------
# Listado con paginación desde el modelo (compatibilidad con development)
# --------------------------------------------------------------------
def list_sites(page: int = 1, per_page: int = 10, filters: dict | None = None):
    base_q = db.session.query(SitioHistorico).order_by(SitioHistorico.id.desc())
    base_q = apply_filters(base_q, filters)
    total = base_q.count()

    items = (
        base_q.offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return items, total


# --------------------------------------------------------------------
# Export CSV con COPY a partir de TU implementación (our changes)
# Mantiene apply_filters + agrega columna "tags" agregada por comas.
# --------------------------------------------------------------------
def export_to_csv(file_path: str, filters: dict | None = None):
    # Subquery de tags concatenados por sitio
    tag_subq = (
        db.session.query(func.string_agg(Tag.name, ", "))
        .select_from(sites_tags.join(Tag, sites_tags.c.tag_id == Tag.id))
        .filter(sites_tags.c.site_id == SitioHistorico.id)
        .correlate(SitioHistorico)
        .scalar_subquery()
    )

    q = db.session.query(
        SitioHistorico.id,
        SitioHistorico.nombre,
        SitioHistorico.descripcionBreve,
        SitioHistorico.estado,
        SitioHistorico.fechaRegistro,
        SitioHistorico.localizacion,
        tag_subq.label("tags"),
    )

    q = apply_filters(q, filters or {})

    if q.count() == 0:
        raise ValueError("No hay datos para exportar con los filtros proporcionados.")

    # COPY a CSV usando conexión raw (PostgreSQL)
    conn = db.engine.raw_connection()
    try:
        cursor = conn.cursor()
        compiled = q.statement.compile(dialect=postgresql.dialect())
        copy_sql = f"COPY ({compiled}) TO STDOUT WITH CSV HEADER"
        with open(file_path, "w", encoding="utf-8") as f:
            cursor.copy_expert(copy_sql, f)
        conn.commit()
    finally:
        conn.close()
