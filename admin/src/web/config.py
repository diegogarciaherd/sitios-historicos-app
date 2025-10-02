from os import environ
from dotenv import load_dotenv
load_dotenv()

class Config:
    TESTING = False
    SECRET_KEY = "your-secret-key"
    SESSION_TYPE = "filesystem"

class ProductionConfig(Config):
    SQLALCHEMY_ENGINES = {
        'default': environ.get('DATABASE_URL')
    }

class DevelopmentConfig(Config):
    DEBUG = True 
    
    # Configuración PostgreSQL para datos geoespaciales
    DB_USER = environ.get("DB_USER", "postgres")
    DB_PASSWORD = environ.get("DB_PASSWORD", "password")
    DB_HOST = environ.get("DB_HOST", "localhost")
    DB_PORT = environ.get("DB_PORT", "5432")
    DB_NAME = environ.get("DB_NAME", "sitios_historicos")
    DB_SCHEME = environ.get("DB_SCHEME", "postgresql")
    SQLALCHEMY_ENGINES = {
        'default': f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }


class TestingConfig(Config):
    TESTING = True

config = { 
    "development" : DevelopmentConfig,
    "production" : ProductionConfig,
    "testing" : TestingConfig,
}