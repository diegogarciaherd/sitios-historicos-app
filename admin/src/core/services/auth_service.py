# src/core/services/auth_service.py
from core.database import db
from core.models.user import User
from core.models.feature_flags import FeatureFlag
from core.services.bcrypt import bcrypt
from flask import session, g
from core.services.auth_roles import has_role
# from werkzeug.security import check_password_hash  # para después hashear

def authenticate(email: str, password: str) -> User | None:
    user = db.session.query(User).filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None

def check_flags(user: User | None):
    flag = db.session.query(FeatureFlag).filter_by(name="Sistema administrativo").first()
    activated = flag.activated if flag else False
    if not activated:
        return False
    if user:
        return not has_role("sys_admin")
    return True

def load_user():
    """Carga el usuario logueado en flask.g antes de cada request."""
    user_id = session.get("user_id")
    g.user = db.session.query(User).filter_by(id=user_id).first() if user_id else None

def get_logged_user():
    """Devuelve el usuario actualmente logueado desde flask.g."""
    return getattr(g, "user", None)
