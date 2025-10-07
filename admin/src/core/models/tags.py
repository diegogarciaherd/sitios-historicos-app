from core.database import Base
from sqlalchemy import String, Integer, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag {self.id}: {self.name}>"
    

def create_tag(name):
    existing_tag = db.session.query(Tag).filter_by(name=name).first()
    if existing_tag:
        return existing_tag  # evita insertar duplicado
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return tag

def assign_tags(site, tags):
    site.tags.extend(tags)
    db.session.commit()
    return site 

def list_tags():
    return db.session.query(Tag).all()