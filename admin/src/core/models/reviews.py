#admin/src/core/models/reviews.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base, db

import enum
class ReviewStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    site_id: Mapped[int] = mapped_column(ForeignKey("sitios_historicos.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)  # opcional

    rating: Mapped[int] = mapped_column(Integer, nullable=False)        # 1..5
    title:  Mapped[str] = mapped_column(String(120), nullable=False)
    body:   Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Moderación
    moderated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relaciones (opcionales para backrefs)
    site = relationship("SitioHistorico", back_populates="reviews", lazy="joined", innerjoin=True)

    def to_dict(self) -> dict:
        """Convierte la reseña a un diccionario"""
        return {
            "id": self.id,
            "site_id": self.site_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "title": self.title,
            "body": self.body,
            "status": (
                self.status.value if isinstance(self.status, enum.Enum) else self.status
            ),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "moderated_by": self.moderated_by,
            "moderated_at": self.moderated_at,
        }

def create_review(**kwargs):
    """
    Crea una nueva reseña a partir de los datos recibidos.

    Args:
        kwargs (dict): Los datos de la nueva reseña.
    
    Returns:
        Review: La reseña creada.
    """
    review = Review(**kwargs)
    db.session.add(review)
    db.session.commit()
    return review

def get_reviews_by_site_id(id: int, page=1, per_page=10):
    """
    Devuelve una lista de todas las reseñas asociadas al sitio
    con id.

    Args:
        id (int): La id del sitio historico.
        page (int): La pagina a mostrar (optional).
        per_page (int): La cantidad de elementos por pagina (optional).

    Returns:
        La lista con las reseñas del sitio historico "id".
    """
    query = db.session.query(Review).filter_by(site_id=id)
    total = query.count()
    reviews = query.offset((int(page) - 1) * int(per_page)).limit(int(per_page)).all()
    return reviews, total

def get_review_by_id(id: int):
    """
    Devuelve una reseña por su clave primaria.

    Args:
        id (int): La id de la reseña.

    Returns:
        La reseña o None.
    """
    return db.session.query(Review).filter_by(id=id).first()

def delete_review(id: int):
    """
    Elimina (fisico) una reseña de la base de datos.

    Args:
        id (int): La id de la reseña a ser eliminada.
    """
    db.session.query(Review).filter_by(id=id).delete()
    db.session.commit()
