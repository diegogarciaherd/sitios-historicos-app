from __future__ import annotations

from datetime import datetime
from typing import Tuple, List, Optional

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base, db

import enum


class ReviewStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sitios_historicos.id"), nullable=False
    )
    # Puede ser None si se permite reseña anónima
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # 1..5
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus),
        default=ReviewStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Moderación
    moderated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    moderated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    reject_reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Relaciones (opcionales para backrefs)
    site = relationship(
        "SitioHistorico",
        back_populates="reviews",
        lazy="joined",
        innerjoin=True,
    )

    def to_dict(self) -> dict:
        """Convierte la reseña a un diccionario simple."""
        return {
            "id": self.id,
            "site_id": self.site_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "title": self.title,
            "body": self.body,
            "status": (
                self.status.value
                if isinstance(self.status, enum.Enum)
                else self.status
            ),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "moderated_by": self.moderated_by,
            "moderated_at": self.moderated_at,
            "reject_reason": self.reject_reason,
        }


def create_review(**kwargs) -> Review:
    """
    Crea una nueva reseña a partir de los datos recibidos.
    """
    review = Review(**kwargs)
    db.session.add(review)
    db.session.commit()
    return review


def get_reviews_by_site_id(
    id: int, page: int = 1, per_page: int = 10
) -> tuple[list[Review], int]:
    """
    Devuelve una lista paginada de reseñas (cualquier estado) para un sitio.
    """
    query = db.session.query(Review).filter_by(site_id=id)
    total = query.count()
    reviews = (
        query.offset((int(page) - 1) * int(per_page))
        .limit(int(per_page))
        .all()
    )
    return reviews, total


def get_reviews_by_user_id(
    user_id: int,
    page: int = 1,
    per_page: int = 25,
    order: str = "desc",
) -> tuple[list[Review], int]:
    """
    Devuelve una lista paginada de reseñas para un usuario dado,
    ordenadas por fecha (asc/desc).
    """
    query = db.session.query(Review).filter(Review.user_id == user_id)

    if order == "asc":
        query = query.order_by(Review.created_at.asc())
    else:
        query = query.order_by(Review.created_at.desc())

    total = query.count()
    reviews = (
        query.offset((int(page) - 1) * int(per_page))
        .limit(int(per_page))
        .all()
    )
    return reviews, total


def get_review_by_id(id: int) -> Optional[Review]:
    """
    Devuelve una reseña por su clave primaria o None.
    """
    return db.session.query(Review).filter_by(id=id).first()


def delete_review(id: int) -> None:
    """
    Elimina (físico) una reseña de la base de datos.
    """
    db.session.query(Review).filter_by(id=id).delete()
    db.session.commit()


# ---------- Helpers para vistas públicas ----------


def get_approved_reviews_for_site(
    site_id: int,
) -> tuple[list[Review], int, Optional[float]]:
    """
    Devuelve las reseñas APROBADAS de un sitio, ordenadas de
    más nueva a más vieja, junto con el total y el promedio de rating.
    """
    # Lista de reseñas aprobadas
    reviews = (
        db.session.query(Review)
        .filter(
            Review.site_id == site_id,
            Review.status == ReviewStatus.APPROVED,
        )
        .order_by(Review.created_at.desc())
        .all()
    )

    total = len(reviews)

    # Promedio de rating (None si no hay reseñas)
    avg = (
        db.session.query(func.avg(Review.rating))
        .filter(
            Review.site_id == site_id,
            Review.status == ReviewStatus.APPROVED,
        )
        .scalar()
    )
    avg_rating = round(float(avg), 1) if avg is not None else None

    return reviews, total, avg_rating
