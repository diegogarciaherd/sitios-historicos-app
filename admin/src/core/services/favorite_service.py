"""
Servicio de favoritos
---------------------
Acá vive la lógica para marcar y desmarcar sitios favoritos
de un usuario, sin meter esa lógica dentro de las vistas.
"""

from core.database import db
from core.models.favorites import Favorite


def toggle_favorite(user_id: int, site_id: int) -> bool:
    """
    Alterna el estado de favorito para un usuario y un sitio.

    - Si ya existe un registro Favorite(user_id, site_id) -> lo elimina.
    - Si no existe -> lo crea.

    Devuelve:
        True  si se creó el favorito.
        False si se eliminó.
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

    new_fav = Favorite(user_id=user_id, site_id=site_id)
    db.session.add(new_fav)
    db.session.commit()
    return True


def get_user_favorites(user_id: int) -> list[Favorite]:
    """
    Devuelve todos los favoritos de un usuario, ordenados del
    más nuevo al más viejo.
    """
    return (
        db.session.query(Favorite)
        .filter_by(user_id=user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
