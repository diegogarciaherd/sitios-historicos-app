from core.database import Base
from sqlalchemy import String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db
from slugify import slugify
from sqlalchemy import func, asc, desc, DateTime
from datetime import datetime


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __init__(self, name):
        self.name = name
        self.slug = self._generate_unique_slug(name)

    def _generate_unique_slug(self, name):
        base_slug = slugify(name)
        slug = base_slug
        counter = 1

        # Verificar si el slug ya existe en la base
        while db.session.query(Tag).filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def __repr__(self):
        return f"<Tag {self.id}: {self.name} ({self.slug})>"


def create_tag(name):
    """Crea un nuevo tag si no existe uno igual."""
    name = name.strip()
    if not (3 <= len(name) <= 50):
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")

    existing = (
        db.session.query(Tag).filter(func.lower(Tag.name) == name.lower()).first()
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
    """
    if not site:
        raise ValueError("El sitio no existe")
    if not isinstance(tag_list, list):
        raise ValueError("tag_list debe ser una lista de objetos Tag")

    site.tags.clear()          # Limpiar tags existentes
    site.tags.extend(tag_list) # Asignar nuevos tags
    db.session.commit()

def list_tags(search=None, page=1, per_page=25):
    """Devuelve los tags, con soporte opcional para búsqueda y paginación."""
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

    new_name = new_name.strip()
    if not (3 <= len(new_name) <= 50):
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")

    existing = (
        db.session.query(Tag)
        .filter(func.lower(Tag.name) == new_name.lower(), Tag.id != tag_id)
        .first()
    )
    if existing:
        raise ValueError("Ya existe un tag con ese nombre.")

    tag.name = new_name
    tag.slug = slugify(new_name)
    db.session.commit()
    return tag


def delete_tag(tag_id, can_delete=True):
    tag = db.session.query(Tag).get(tag_id)
    if not tag or not can_delete:
        return None
    db.session.delete(tag)
    db.session.commit()
    return tag


def get_tags_paginated(page=1, per_page=10, search=""):
    query = db.session.query(Tag)

    if search:
        query = query.filter(func.lower(Tag.name).like(f"%{search.lower()}%"))

    total = query.count()
    tags = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    return tags, total, total_pages


def get_tags(search="", order_by="name_asc", page=1, per_page=10):
    # Base query
    query = db.session.query(Tag)

    # Filtro por búsqueda
    if search:
        query = query.filter(func.lower(Tag.name).like(f"%{search.lower()}%"))

    # Orden
    if order_by == "name_asc":
        query = query.order_by(Tag.name.asc())
    elif order_by == "name_desc":
        query = query.order_by(Tag.name.desc())
    elif order_by == "date_asc":
        query = query.order_by(Tag.created_at.asc())
    elif order_by == "date_desc":
        query = query.order_by(Tag.created_at.desc())

    # Total de resultados
    total = query.count()

    # Paginación
    offset = (page - 1) * per_page
    tags = query.offset(offset).limit(per_page).all()

    # Total de páginas
    total_pages = (total + per_page - 1) // per_page

    return tags, total, total_pages

def get_all_tags():
    return db.session.query(Tag).order_by(Tag.name.asc()).all()
