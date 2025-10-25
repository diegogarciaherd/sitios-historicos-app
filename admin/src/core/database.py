# admin/src/core/database.py
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

'''Módulo de configuración e inicialización de la base de datos'''

db = SQLAlchemy()

def init_app(app):
    '''Inicializa la base de datos con la app Flask'''
    db.init_app(app)
    return db

class Base(DeclarativeBase):
    '''Clase base para los modelos de la base de datos'''
    pass

def reset_db():
    '''Elimina y crea todas las tablas de la base de datos'''
    from core.models.sites import SitioHistorico
    from core.models.user import User
    from core.models.feature_flags import FeatureFlag
    from core.models.feature_flags_history import FeatureFlagHistory
    from core.models.auth import Role, Permission, RolePermission, UserRole, BlockedUser, LogicallyDeletedUser
    from core.models.tags import Tag

    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")

def seed_db():
    '''Ejecuta los seeders para poblar la base de datos con datos iniciales'''
    from core import seeds_roles
    from core import seeds
    print("Seeding database...")
    seeds_roles.run()
    seeds.run()
    print("Database seeding complete.")

def ping_db() -> bool:
    '''Verifica la conexión con la base de datos'''
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Ping fallido: {e}")
        return False

