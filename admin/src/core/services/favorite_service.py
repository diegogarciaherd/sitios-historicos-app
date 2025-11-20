# admin/src/core/services/favorite_service.py

from core.database import db
from core.models.favorites import Favorite


def toggle_favorite(user_id: int, site_id: int) -> bool:
    """
    Alterna el favorito. Si existe lo borra, si no, lo crea.
    Devuelve True si se creó, False si se eliminó.
    """
    fav = (
        db.session.query(Favorite)
        .filter_by(user_id=user_id, site_id=site_id)
        .first()
    )

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return False

    new = Favorite(user_id=user_id, site_id=site_id)
    db.session.add(new)
    db.session.commit()
    return True


def get_user_favorites(user_id: int):
    """
    Devuelve todos los favoritos del usuario ordenados del más nuevo
    al más antiguo.
    """
    return (
        db.session.query(Favorite)
        .filter_by(user_id=user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
