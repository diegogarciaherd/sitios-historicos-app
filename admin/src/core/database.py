# admin/src/core/database.py
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    return db

class Base(DeclarativeBase):
    pass

def reset_db():
    from core.models.sites import SitioHistorico
    from core.models.user import User
    from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser

    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")

def seed_db():
    from core import seeds_roles
    from core import seeds
    print("Seeding database...")
    seeds_roles.run()
    seeds.run()
    print("Database seeding complete.")

def ping_db() -> bool:
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Ping fallido: {e}")
        return False

