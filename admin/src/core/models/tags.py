from core.database import Base
from sqlalchemy import String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db
from slugify import slugify
from sqlalchemy import func

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

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
    
    existing = db.session.query(Tag).filter(func.lower(Tag.name) == name.lower()).first()
    if existing:
        raise ValueError("Ya existe un tag con ese nombre.")
    
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return tag

def assign_tags(site, tags):
    site.tags.extend(tags)
    db.session.commit()
    return site 

def list_tags(search=None, page=1, per_page=25):
    """Devuelve los tags, con soporte opcional para búsqueda y paginación."""
    query = db.session.query(Tag)
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    pagination = query.order_by(Tag.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return pagination

def update_tag(tag_id, new_name):
    """Actualiza un tag existente."""
    tag = db.session.query(Tag).get(tag_id)
    if not tag:
        raise ValueError("Tag no encontrado.")
    
    new_name = new_name.strip()
    if not (3 <= len(new_name) <= 50):
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")
    
    existing = db.session.query(Tag).filter(func.lower(Tag.name) == new_name.lower(), Tag.id != tag_id).first()
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

def get_tags_paginated(page=1, per_page=10):
    total = db.session.query(Tag).count()
    offset = (page - 1) * per_page
    items = db.session.query(Tag).order_by(Tag.name.asc()).limit(per_page).offset(offset).all()
    total_pages = (total + per_page - 1) // per_page
    return items, total, total_pages