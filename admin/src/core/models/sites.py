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

# Tabla de asociación
''' Tabla de asociación entre sitios históricos y tags ''' 
''' atributos: 
     id: Identificador único de la asociación
     site_id: Identificador del sitio histórico
     tag_id: Identificador del tag asociado
     '''
sites_tags = Table(
    "sites_tags",
    Base.metadata,
    Column("site_id", Integer, ForeignKey("sitios_historicos.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class EstadoConservacion(enum.Enum):
    '''Enum para el estado de conservación de un sitio histórico'''
    BUENO = "Bueno"
    REGULAR = "Regular"
    MALO = "Malo"


class SitioHistorico(Base):
    '''Modelo de Sitio Histórico'''
  
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
        backref="sitios_historicos",  # backref en lugar de back_populates
        lazy="select",
    )
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    localizacion: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    @property
    def lat(self) -> float:
        '''Devuelve la latitud del sitio
        '''
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
            "tags": [tag.to_dict() for tag in self.tags],
        }


def list_sites(page=1, per_page=10):
    '''Lista todos los sitios históricos con paginación.'''
    query = db.session.query(SitioHistorico)
    total = query.count()
    sites = query.offset((page - 1) * per_page).limit(per_page).all()
    return sites, total


def list_sites_with_filters(filters, page=1, per_page=10):
    """Lista sitios históricos aplicando filtros opcionales."""

    query = db.session.query(SitioHistorico)
    query = apply_filters(query, filters)
    total = query.count()
    sites = query.offset((int(page) - 1) * int(per_page)).limit(int(per_page)).all()
    return sites, total


def get_all_provinces():
    """Devuelve una lista de todas las provincias únicas en la base de datos."""
    return db.session.query(SitioHistorico.provincia).distinct().all()


def get_all_cities():
    """Devuelve una lista de todas las ciudades únicas en la base de datos."""
    return db.session.query(SitioHistorico.ciudad).distinct().all()


def create_sites(**kwargs):
    '''Crea un nuevo sitio historico'''
    ''' params : kwargs: diccionario con los atributos del sitio historico'''


    # Extraer y convertir coordenadas
    lat = kwargs.pop("lat", None)
    lng = kwargs.pop("lng", None)

    kwargs["estado"] = kwargs["estado"].upper()

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
    '''Actualiza un sitio historico existente'''
    ''' params : id: id del sitio a actualizar
        kwargs: diccionario con los atributos a actualizar
    '''
    
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
    '''Obtiene un sitio historico por su id'''
    return db.session.query(SitioHistorico).filter(SitioHistorico.id == id).first()


def delete_site_by_id(id):
    '''Elimina un sitio historico por su id'''
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
            pass

    if "tags" in filters and filters["tags"]:
        # Filtrar por tags (lista de nombres de tags)
        # Por cada sitio en la query se debe verificar que tenga almenos uno de los tags en la lista filters["tags"]

        # Convertimos los tags a una lista porque es un string separado por comas
        if isinstance(filters["tags"], str):
            filters["tags"] = [tag.strip() for tag in filters["tags"].split(",")]

        query = query.filter(SitioHistorico.tags.any(Tag.name.in_(filters["tags"])))

    if "order_by" in filters and filters["order_by"]:
        match filters["order_by"]:
            #Todavia no hay una columna o tabla aparte de rating, cuando haya,
            #se descomenta esto
            #case "rating-5-1":
            #    query = query.order_by(SitioHistorico.rating.desc())
            #case "rating-1-5:":
            #    query = query.order_by(SitioHistorico.rating.asc())
            case "latest":
                query = query.order_by(SitioHistorico.fechaRegistro.asc())
            case "oldest":
                query = query.order_by(SitioHistorico.fechaRegistro.desc())

    if "lat" in filters and filters["lat"]:
        query = query.filter(lat=filters["lat"])

    if "long" in filters and filters["long"]:
        query = query.filter(long=filters["long"])

    return query

def get_sites_by_tag(tag_id: int):
    """Devuelve todos los sitios asociados a un tag dado."""
    return db.session.query(SitioHistorico).filter(SitioHistorico.tags.any(id=tag_id)).all()