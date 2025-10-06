from core.database import db
from core.models.user import User
from core.models.feature_flags import FeatureFlag
from werkzeug.security import check_password_hash
from flask import redirect, url_for

def authenticate(email: str, password: str) -> User:
    user = db.session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def check_flags(user: User):
    flag = db.session.query(FeatureFlag).filter_by(name="Sitio administrativo").first()
    return flag.activated if flag else False