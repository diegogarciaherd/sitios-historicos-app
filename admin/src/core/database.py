from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text 

db = SQLAlchemy()

def init_app(app):
    db.init_app(app) # Recibe la app de Flask y la configura con SQLAlchemy

    return db

def reset_db():
    from core.models.sites import SitioHistorico
    from core.models.user import User
    from core.models.tags import Tag
    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")

def seed_db():
    from core import seeds
    print("Seeding database...")
    seeds.run()
    print("Database seeding complete.")

    
class Base(DeclarativeBase):
    pass
    

def ping_db() -> bool:
    """Devuelve True si la conexión a la BD responde."""
    try:
        db.session.execute(text("SELECT 1"))  # usa la conexión ya inicializada
        return True
    except Exception as e:
        print(f"[DB] Ping fallido: {e}")
        return False