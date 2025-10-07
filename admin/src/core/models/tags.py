from core.database import Base
from sqlalchemy import String, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from core.models.sites import sites_tags

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    sites = relationship("Site", secondary=sites_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.id}: {self.name}>"