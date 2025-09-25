from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

def init_app(app):
    db.init_app(app) # Recibe la app de Flask y la configura con SQLAlchemy 
    
    return db

def reset_db():
    from src.core.models.sites import SitioHistorico
    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")

def seed_db():
    from src.core import seeds
    print("Seeding database...")
    seeds.run()
    print("Database seeding complete.")

    
class Base(DeclarativeBase):
    pass
    