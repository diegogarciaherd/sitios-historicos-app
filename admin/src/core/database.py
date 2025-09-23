from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

def init_app(app):
    db.init_app(app) # Recibe la app de Flask y la configura con SQLAlchemy 
    
    return db

class Base(DeclarativeBase):
    pass
    