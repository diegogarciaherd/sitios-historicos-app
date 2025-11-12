# admin/src/core/models/tags.py
from core.database import Base, db
from sqlalchemy import String, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import re


def _simple_slugify(text: str) -> str:
    """
    Genera un slug simple:
    - pasa a minúsculas
    - reemplaza cualquier cosa no alfanumérica por '-'
    - colapsa guiones repetidos
    - recorta guiones al inicio/fin
    """
    text = str(text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "tag"


class Tag(Base):
    """
    Modelo de Tag para categorizar sitios históricos.

    Atributos:
        id: Identificador único del tag
        name: Nombre del tag
        slug: Versión amigable para URLs del nombre
        created_at: Fecha de creación del tag
    """
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __init__(self, name: str):
        self.name = name.strip()
        self.slug = self._generate_unique_slug(self.name)

    def _generate_unique_slug(self, name: str) -> str:
        """
        Genera un slug único basado en el nombre.
        Si el slug existe, agrega -1, -2, etc.
        """
        base_slug = _simple_slugify(name)
        slug = base_slug
        counter = 1

        while db.session.query(Tag).filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def to_dict(self) -> dict:
        """Convierte el tag a un diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
        }

    def __repr__(self) -> str:
        return f"<Tag {self.id}: {self.name} ({self.slug})>"


# ---------- Helpers de dominio ----------

def create_tag(name: str):
    """Crea un nuevo tag si no existe uno igual."""
    name = (name or "").strip()
    if not (3 <= len(name) <= 50):
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")

    existing = (
        db.session.query(Tag)
        .filter(func.lower(Tag.name) == name.lower())
        .first()
    )
    if existing:
        raise ValueError("Ya existe un tag con ese nombre.")

    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return tag


def assign_tags(site, tag_list):
    """
    Asigna una lista de objetos Tag a un sitio histórico.
    Reemplaza completamente los tags actuales.
    """
    if not site:
        raise ValueError("El sitio no existe")
    if not isinstance(tag_list, list):
        raise ValueError("tag_list debe ser una lista de objetos Tag")

    site.tags.clear()
    site.tags.extend(tag_list)
    db.session.commit()


def list_tags(search=None, page=1, per_page=25):
    """
    Devuelve los tags, con soporte opcional para búsqueda y paginación.
    Retorna (tags, total, total_pages).
    """
    query = db.session.query(Tag)

    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))

    total = query.count()
    tags = (
        query.order_by(Tag.name.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    total_pages = (total + per_page - 1) // per_page

    return tags, total, total_pages


def update_tag(tag_id, new_name):
    """Actualiza un tag existente."""
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        raise ValueError("Tag no encontrado.")

    new_name = (new_name or "").strip()
    if not (3 <= len(new_name) <= 50):
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")

    existing = (
        db.session.query(Tag)
        .filter(
            func.lower(Tag.name) == new_name.lower(),
            Tag.id != tag_id
        )
        .first()
    )
    if existing:
        raise ValueError("Ya existe un tag con ese nombre.")

    tag.name = new_name
    tag.slug = tag._generate_unique_slug(new_name)
    db.session.commit()
    return tag


def delete_tag(tag_id, can_delete=True):
    """Elimina un tag por su ID si es posible."""
    tag = db.session.query(Tag).get(tag_id)
    if not tag or not can_delete:
        return None
    db.session.delete(tag)
    db.session.commit()
    return tag


def get_tags_paginated(page=1, per_page=10, search=""):
    """Obtiene tags con paginación y búsqueda opcional."""
    query = db.session.query(Tag)

    if search:
        query = query.filter(func.lower(Tag.name).like(f"%{search.lower()}%"))

    total = query.count()
    tags = (
        query.offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    total_pages = (total + per_page - 1) // per_page

    return tags, total, total_pages


def get_tags(search="", order_by="name_asc", page=1, per_page=10):
    """
    Obtiene tags con búsqueda, orden y paginación.
    order_by: name_asc, name_desc, date_asc, date_desc
    """
    query = db.session.query(Tag)

    if search:
        query = query.filter(func.lower(Tag.name).like(f"%{search.lower()}%"))

    if order_by == "name_asc":
        query = query.order_by(Tag.name.asc())
    elif order_by == "name_desc":
        query = query.order_by(Tag.name.desc())
    elif order_by == "date_asc":
        query = query.order_by(Tag.created_at.asc())
    elif order_by == "date_desc":
        query = query.order_by(Tag.created_at.desc())

    total = query.count()
    offset = (page - 1) * per_page
    tags = query.offset(offset).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    return tags, total, total_pages


def get_all_tags():
    """Obtiene todos los tags sin paginación ordenados por nombre ascendente."""
    return db.session.query(Tag).order_by(Tag.name.asc()).all()


def get_tags_by_ids(tag_ids):
    """Obtiene una lista de tags dado una lista de IDs."""
    return db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()


def get_tag_by_id(tag_id):
    """Obtiene un tag por su ID."""
    return db.session.query(Tag).get(tag_id)
