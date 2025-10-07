from core.database import Base, db
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects import postgresql


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
            return punto.y  # Latitud
        return None

    @property
    def lng(self) -> float:
        "Devuelve la longitud del sitio"
        if self.localizacion:
            punto = to_shape(self.localizacion)
            return punto.x  # Longitud
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
        }


def list_sites(page=1, per_page=10):
    query = db.session.query(SitioHistorico)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total


def list_sites_with_filters(filters, page=1, per_page=10):
    """Lista sitios históricos aplicando filtros opcionales."""

    query = db.session.query(SitioHistorico)
    query = apply_filters(query, filters)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total


def get_all_provinces():
    """Devuelve una lista de todas las provincias únicas en la base de datos."""
    return db.session.query(SitioHistorico.provincia).distinct().all()


def get_all_cities():
    """Devuelve una lista de todas las ciudades únicas en la base de datos."""
    return db.session.query(SitioHistorico.ciudad).distinct().all()


def create_sites(**kwargs):
    # Extraer y convertir coordenadas
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    # Convertir año si existe
    año_inauguracion = kwargs.get("añoInauguracion")
    if año_inauguracion:
        kwargs["añoInauguracion"] = int(año_inauguracion)

    # Crear el sitio
    site = SitioHistorico(**kwargs)

    # Asignar geometría si hay coordenadas
    if lat is not None and lng is not None:
        site.localizacion = WKTElement(f"POINT({float(lng)} {float(lat)})", srid=4326)

    db.session.add(site)
    db.session.commit()
    return site


def update_site(id, **kwargs):
    site = get_site(id)
    if not site:
        raise ValueError(f"Sitio con id {id} no encontrado")

    # Extraer coordenadas si vienen en kwargs
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    # Convertir año si existe
    año_inauguracion = kwargs.get("añoInauguracion")
    if año_inauguracion is not None:
        if año_inauguracion == "":
            kwargs["añoInauguracion"] = None
        else:
            try:
                kwargs["añoInauguracion"] = int(año_inauguracion)
            except (ValueError, TypeError):
                raise ValueError("El año de inauguración debe ser un número válido")

    # Actualizar atributos
    for key, value in kwargs.items():
        if hasattr(site, key):
            setattr(site, key, value)

    # Actualizar geometría si hay nuevas coordenadas
    if lat is not None and lng is not None:
        try:
            site.localizacion = WKTElement(
                f"POINT({float(lng)} {float(lat)})", srid=4326
            )
            # También actualizar latitud y longitud por separado si existen en tu modelo
            if hasattr(site, "latitud"):
                site.latitud = float(lat)
            if hasattr(site, "longitud"):
                site.longitud = float(lng)
        except (ValueError, TypeError):
            raise ValueError("Las coordenadas deben ser números válidos")

    db.session.commit()
    return site


def get_site(id):
    return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first()


def delete_site_by_id(id):
    site = get_site(id)
    db.session.delete(site)
    db.session.commit()
    return site


def apply_filters(query, filters):
    """Aplica filtros a una consulta de sitios históricos."""

    if "search" in filters and filters["search"]:
        # Búsqueda por texto: El texto debe estar contenido en el nombre del sitio o la descripción breve
        search_term = f"%{filters['search']}%"
        query = query.filter(
            (SitioHistorico.nombre.ilike(search_term))
            | (SitioHistorico.descripcionBreve.ilike(search_term))
        )

    if "city" in filters and filters["city"]:
        # El valor de ciudad debe coincidir exactamente (case-insensitive)
        query = query.filter(SitioHistorico.ciudad.ilike(filters["city"]))

    if "province" in filters and filters["province"]:
        # El valor de provincia debe coincidir exactamente (case-insensitive)
        query = query.filter(SitioHistorico.provincia.ilike(filters["province"]))

    if "status" in filters and filters["status"]:
        # Filtrar por estado de conservación
        try:
            estado_enum = EstadoConservacion[filters["status"].upper()]
            query = query.filter(SitioHistorico.estado == estado_enum)
        except KeyError:
            pass  # Si el estado no es válido, no aplicar el filtro

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
            pass  # Si la fecha no es válida, no aplicar el filtro

    if "endDate" in filters and filters["endDate"]:
        try:
            end_date = datetime.strptime(filters["endDate"], "%Y-%m-%d")
            query = query.filter(SitioHistorico.fechaRegistro <= end_date)
        except ValueError:
            pass  # Si la fecha no es válida, no aplicar el filtro

    return query


def export_to_csv(file_path: str, filters: dict = None):
    """Exporta los sitios históricos a un archivo CSV aplicando filtros opcionales usando POSTGRE COPY."""

    query = db.session.query(
        SitioHistorico.id,
        SitioHistorico.nombre,
        SitioHistorico.descripcionBreve,
        SitioHistorico.ciudad,
        SitioHistorico.provincia,
        SitioHistorico.estado,
        SitioHistorico.fechaRegistro,
        SitioHistorico.localizacion,
        # proximamente incluir tags
    )
    query = apply_filters(query, filters)

    # Ordenar los resultaos por fecha de registro, nombre o ciudad (asc/desc).
    # Primero por fecha de registro descendente (los más recientes primero)
    # En caso de empate, por nombre ascendente (A-Z)
    # En caso de nuevo empate, por ciudad ascendente (A-Z)
    query = query.order_by(
        SitioHistorico.fechaRegistro.desc(),
        SitioHistorico.nombre.asc(),
        SitioHistorico.ciudad.asc(),
    )

    # verificar si hay resultados
    if query.count() == 0:
        raise ValueError("No hay datos para exportar con los filtros proporcionados.")

    query_compiled = query.statement.compile(
        dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
    )

    with open(file_path, "w", encoding="utf-8") as csvfile:
        # Usar el método COPY de PostgreSQL para exportar directamente a CSV
        connection = db.session.connection().connection
        cursor = connection.cursor()
        try:
            sql = f"COPY ({str(query_compiled)}) TO STDOUT WITH CSV HEADER"
            cursor.copy_expert(sql, csvfile)
        finally:
            cursor.close()
