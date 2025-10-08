# src/core/services/auth_service.py
from core.database import db
from core.models.user import User
from core.models.feature_flags import FeatureFlag
from flask import session, g
# from werkzeug.security import check_password_hash  # para después hashear

def authenticate(email: str, password: str) -> User | None:
    user = db.session.query(User).filter_by(email=email).first()
    # if user and check_password_hash(user.password, password):
    if user:  # por ahora sin hash
        return user
    return None

def check_flags(user: User | None) -> bool:
    flag = db.session.query(FeatureFlag).filter_by(name="Sitio administrativo").first()
    return bool(flag and flag.activated)

def load_user():
    """Carga el usuario logueado en flask.g antes de cada request."""
    user_id = session.get("user_id")
    g.user = db.session.query(User).filter_by(id=user_id).first() if user_id else None

def get_logged_user():
    """Devuelve el usuario actualmente logueado desde flask.g."""
    return getattr(g, "user", None)
