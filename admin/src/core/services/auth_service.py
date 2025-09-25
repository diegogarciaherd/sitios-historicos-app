from core.database import db
from core.models.user import User
from werkzeug.security import check_password_hash

def authenticate(email: str, password: str) -> User:
    user = db.session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None
