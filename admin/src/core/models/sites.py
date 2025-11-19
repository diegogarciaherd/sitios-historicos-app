# admin/src/core/models/sites.py

from core.database import Base, db
import enum
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from core.models.tags import Tag

from typing import TYPE_CHECKING

# TYPE_CHECKING para evitar imports circulares en runtime
if TYPE_CHECKING:
    from core.models.reviews import Review  # solo hints
    from core.models.favorites import Favorite  # hints para la relación de favoritos


# ----------------------------------------------------
# Tabla de asociación sitios <-> tags (many-to-many)
# ----------------------------------------------------
# No hace falta modelo propio, con esta tabla de asociación alcanza.


sites_tags = Table(
    "sites_tags",
    Base.metadata,
    Column("site_id", Integer, ForeignKey("sitios_historicos.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class EstadoConservacion(enum.Enum):
    """Enum de estado de conservación de un sitio histórico.

    Lo guardamos como texto legible y validamos contra estos valores.
    """

    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"


class SitioHistorico(Base):
    """Modelo principal de sitio histórico.

    Esta es la entidad que después ve el usuario en el portal.
    Acá van todos los datos "duros" del sitio (descripciones, ubicación,
    estado, etc.) y las relaciones con tags, reseñas y favoritos.
    """

    __tablename__ = "sitios_historicos"

    # -------------------------------
    # Campos básicos del sitio
    # -------------------------------
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcionBreve: Mapped[str] = mapped_column(Text, nullable=True)
    descripcionCompleta: Mapped[str] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=True)
    provincia: Mapped[str] = mapped_column(String(100), nullable=True)

    # Estado de conservación (usamos enum de arriba)
    estado: Mapped[EstadoConservacion] = mapped_column(
        Enum(EstadoConservacion, native_enum=False, validate_strings=True),
        nullable=False,
    )

    añoInauguracion: Mapped[int] = mapped_column(Integer, nullable=True)
    categoria: Mapped[str] = mapped_column(Text, nullable=True)

    # Cuándo se registró en el sistema (no cuándo se inauguró)
    fechaRegistro: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # -------------------------------
    # Relaciones con otras entidades
    # -------------------------------

    # Tags asociados (many-to-many)
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=sites_tags,
        backref="sitios_historicos",
        lazy="select",
    )

    # Reseñas que los usuarios dejaron sobre el sitio
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="site",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Favoritos: todos los registros de usuarios que marcaron este sitio
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="site",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # -------------------------------
    # Otros campos
    # -------------------------------
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Punto geográfico (srid=4326 para trabajar en lat/lng)
    localizacion: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # -------------------------------
    # Helpers para lat / lng
    # -------------------------------
    @property
    def lat(self) -> float | None:
        """Devuelve la latitud del sitio a partir de la geometría."""
        if self.localizacion:
            punto = to_shape(self.localizacion)
            return punto.y
        return None

    @property
    def lng(self) -> float | None:
        """Devuelve la longitud del sitio a partir de la geometría."""
        if self.localizacion:
            punto = to_shape(self.localizacion)
            return punto.x
        return None

    # -------------------------------
    # Serialización a dict para APIs
    # -------------------------------
    def to_dict(self) -> dict:
        """Convierte el sitio a un diccionario listo para enviar por JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcionBreve": self.descripcionBreve,
            "descripcionCompleta": self.descripcionCompleta,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "estado": (
                self.estado.value if isinstance(self.estado, enum.Enum) else self.estado
            ),
            "añoInauguracion": self.añoInauguracion,
            "categoria": self.categoria,
            "lat": self.lat,
            "lng": self.lng,
            "fechaRegistro": (
                self.fechaRegistro.isoformat() if self.fechaRegistro else None
            ),
            "visible": self.visible,
            "tags": [tag.to_dict() for tag in self.tags],
        }


# --------------------------------------------------------------------
# Funciones helper de consulta / creación / actualización de sitios
# --------------------------------------------------------------------

def list_sites(page: int = 1, per_page: int = 10):
    """Lista todos los sitios históricos con paginación simple.

    Devuelve (sites, total) donde:
    - sites es la página actual
    - total es la cantidad total de sitios
    """
    query = db.session.query(SitioHistorico)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total


def list_sites_with_filters(filters: dict, page: int = 1, per_page: int = 10):
    """Lista sitios aplicando los filtros que vienen del portal público."""
    query = db.session.query(SitioHistorico)
    query = apply_filters(query, filters)
    total = query.count()
    sites = query.offset((int(page) - 1) * int(per_page)).limit(int(per_page)).all()
    return sites, total


def get_all_provinces():
    """Devuelve una lista de provincias únicas (para armar filtros en el front)."""
    return db.session.query(SitioHistorico.provincia).distinct().all()


def get_all_cities():
    """Devuelve una lista de ciudades únicas (para armar filtros en el front)."""
    return db.session.query(SitioHistorico.ciudad).distinct().all()


def create_sites(**kwargs):
    """Crea un nuevo sitio histórico a partir de los datos del formulario admin.

    Acá también se encarga de transformar valores "de front" a lo que
    espera el modelo (ej: lat/lng en WKT, año como int, etc.).
    """

    # Extraigo coordenadas porque después las uso para el WKT
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    # Normalizo el estado para matchear con el enum
    kwargs["estado"] = kwargs["estado"].upper()

    # Convierto el año de inauguración si viene
    año_inauguracion = kwargs.get("añoInauguracion")
    if año_inauguracion:
        kwargs["añoInauguracion"] = int(año_inauguracion)

    # Creo el sitio con los campos relevantes
    site = SitioHistorico(
        nombre=kwargs.get("nombre"),
        descripcionBreve=kwargs.get("descripcionBreve"),
        descripcionCompleta=kwargs.get("descripcionCompleta"),
        ciudad=kwargs.get("ciudad"),
        provincia=kwargs.get("provincia"),
        estado=kwargs.get("estado"),
        añoInauguracion=kwargs.get("añoInauguracion"),
        categoria=kwargs.get("categoria"),
        visible=kwargs.get("visible", True),
    )

    # Si tengo coordenadas, armo el POINT
    if lat is not None and lng is not None:
        site.localizacion = WKTElement(f"POINT({float(lng)} {float(lat)})", srid=4326)

    db.session.add(site)
    db.session.commit()
    return site


def update_site(id: int, **kwargs):
    """Actualiza un sitio histórico existente.

    Solo pisa los campos que vienen en kwargs y valida año y coordenadas.
    """

    site = get_site(id)
    if not site:
        raise ValueError(f"Sitio con id {id} no encontrado")

    # Coordenadas que puedan venir de un formulario
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    # Año de inauguración: puede venir vacío, None o string numérico
    año_inauguracion = kwargs.get("añoInauguracion")
    if año_inauguracion is not None:
        if año_inauguracion == "":
            kwargs["añoInauguracion"] = None
        else:
            try:
                kwargs["añoInauguracion"] = int(año_inauguracion)
            except (ValueError, TypeError):
                raise ValueError("El año de inauguración debe ser un número válido")

    # Actualizo solo atributos que realmente existen en el modelo
    for key, value in kwargs.items():
        if hasattr(site, key):
            setattr(site, key, value)

    # Si vinieron coords nuevas, actualizo la geometría
    if lat is not None and lng is not None:
        try:
            site.localizacion = WKTElement(
                f"POINT({float(lng)} {float(lat)})", srid=4326
            )
            # Campos latitud/longitud separados, si existen
            if hasattr(site, "latitud"):
                site.latitud = float(lat)
            if hasattr(site, "longitud"):
                site.longitud = float(lng)
        except (ValueError, TypeError):
            raise ValueError("Las coordenadas deben ser números válidos")

    db.session.commit()
    return site


def get_site(id: int) -> SitioHistorico | None:
    """Devuelve un sitio por id o None si no existe."""
    return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first()


def delete_site_by_id(id: int) -> SitioHistorico:
    """Elimina físicamente un sitio histórico por id."""
    site = get_site(id)
    db.session.delete(site)
    db.session.commit()
    return site


def apply_filters(query, filters: dict):
    """Aplica sobre la query los filtros que llegan desde el portal público.

    Acá vive toda la lógica de búsqueda y ordenamiento, así aislamos
    la complejidad y el endpoint queda más limpio.
    """

    if "search" in filters and filters["search"]:
        # Texto libre: busca en nombre y descripción breve
        search_term = f"%{filters['search']}%"
        query = query.filter(
            (SitioHistorico.nombre.ilike(search_term))
            | (SitioHistorico.descripcionBreve.ilike(search_term))
        )

    if "city" in filters and filters["city"]:
        query = query.filter(SitioHistorico.ciudad.ilike(filters["city"]))

    if "province" in filters and filters["province"]:
        query = query.filter(SitioHistorico.provincia.ilike(filters["province"]))

    if "status" in filters and filters["status"]:
        try:
            estado_enum = EstadoConservacion[filters["status"].upper()]
            query = query.filter(SitioHistorico.estado == estado_enum)
        except KeyError:
            # Si viene algo inválido, simplemente ignoramos ese filtro
            pass

    # Si no mandan visibility, por defecto mostramos solo visibles
    if "visibility" in filters:
        visibility = filters["visibility"].lower() == "true"
    else:
        visibility = True
    query = query.filter(SitioHistorico.visible == visibility)

    if "startDate" in filters and filters["startDate"]:
        try:
            start_date = datetime.strptime(filters["startDate"], "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro >= start_date)
        except ValueError:
            pass

    if "endDate" in filters and filters["endDate"]:
        try:
            end_date = datetime.strptime(filters["endDate"], "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro <= end_date)
        except ValueError:
            pass

    if "tags" in filters and filters["tags"]:
        # Los tags pueden venir como string "tag1,tag2" → los paso a lista
        if isinstance(filters["tags"], str):
            filters["tags"] = [tag.strip() for tag in filters["tags"].split(",")]

        query = query.filter(SitioHistorico.tags.any(Tag.name.in_(filters["tags"])))

    # Ordenamiento configurable desde el portal
    if "order_by" in filters and filters["order_by"]:
        match filters["order_by"]:
            case "latest":
                query = query.order_by(SitioHistorico.fechaRegistro.asc())
            case "oldest":
                query = query.order_by(SitioHistorico.fechaRegistro.desc())
            case "name-asc":
                query = query.order_by(SitioHistorico.nombre.asc())
            case "name-desc":
                query = query.order_by(SitioHistorico.nombre.desc())

    # Filtros de lat/long crudos (todavía poco usados)
    if "lat" in filters and filters["lat"]:
        query = query.filter(lat=filters["lat"])

    if "long" in filters and filters["long"]:
        query = query.filter(long=filters["long"])

    return query


def get_sites_by_tag(tag_id: int):
    """Devuelve todos los sitios que tienen asociado el tag indicado."""
    return (
        db.session.query(SitioHistorico)
        .filter(SitioHistorico.tags.any(id=tag_id))
        .all()
    )
