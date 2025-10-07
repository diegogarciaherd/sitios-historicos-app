from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from core.models.userrole import UserRole as Role
from core.database import db
from core.services.bcrypt import bcrypt

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False, default=True)
    role: Mapped[Role] = mapped_column(nullable=False, default=Role.PUBLIC)

    def __repr__(self):
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}, {self.role}>"

def create_user(**kwargs):
    email = kwargs["email"]
    existente = db.session.query(User).filter_by(email=email).first()
    if existente:
        return False
    else:
        kwargs["password"] = bcrypt.generate_password_hash(kwargs["password"]).decode("utf-8")
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return True
    
def get_user_by_id(id):
    return db.session.query(User).filter_by(id=id).first()

def read_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()

def read_users_by_activeness(active):
    return db.session.query(User).filter_by(active=active)

def read_users_by_role(role):
    return db.session.query(User).filter_by(role=role)

def update_user(id, values):
    db.session.query(User).filter_by(id=id).update(values)
    db.session.commit()

def delete_user(id):
    db.session.query(User).filter_by(id=id).delete()
    db.session.commit()

def list_all_users(page=1, per_page=10):
    query = db.session.query(User)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return users, total
