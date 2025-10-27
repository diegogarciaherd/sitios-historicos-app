from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import db
from core.services.bcrypt import bcrypt
from core.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.feature_flags_history import FeatureFlagHistory

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=True, default=True)
    sys_admin: Mapped[bool] = mapped_column(nullable=True, default=False)    
    feature_flags_history: Mapped["FeatureFlagHistory"] = relationship(
        "FeatureFlagHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Usuario {self.id}: {self.email}, {self.name}, {self.last_name}, {self.active}, {self.role}, {self.sys_admin}>"

def create_user(**kwargs):
    email = kwargs["email"]
    existente = db.session.query(User).filter_by(email=email).first()
    if existente:
        return None
    else:
        kwargs["password"] = bcrypt.generate_password_hash(kwargs["password"]).decode("utf-8")
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user
    
def get_user_by_id(id):
    return db.session.query(User).filter_by(id=id).first()

def read_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()

def read_users_by_activeness(active, page=1, per_page=10):
    query = db.session.query(User).filter_by(active=active)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return users, total

def read_users_by_role(role, page=1, per_page=10):
    query = db.session.query(User).filter_by(role=role)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return users, total

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
