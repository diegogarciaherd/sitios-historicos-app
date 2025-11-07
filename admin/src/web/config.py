from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base para la aplicación Flask."""

    TESTING = False
    SECRET_KEY = "your-secret-key"
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    """Configuración para entorno de producción"""

    # Configuracion para Minio
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True
    MINIO_BUCKET = "grupo45"

    # Configuracion para PostgreSQL
    SQLALCHEMY_ENGINES = {"default": environ.get("DATABASE_URL")}


class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""

    DEBUG = True

    # Configuracion para Minio
    MINIO_SERVER = "localhost:9000"
    MINIO_ACCESS_KEY = ""
    MINIO_SECRET_KEY = ""
    MINIO_SECURE = False
    MINIO_BUCKET = "grupo45"

    # Configuración PostgreSQL para datos geoespaciales
    DB_USER = environ.get("DB_USER", "postgres")
    DB_PASSWORD = environ.get("DB_PASSWORD", "password")
    DB_HOST = environ.get("DB_HOST", "localhost")
    DB_PORT = environ.get("DB_PORT", "5432")
    DB_NAME = environ.get("DB_NAME", "sitios_historicos")
    DB_SCHEME = environ.get("DB_SCHEME", "postgresql")
    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }


class TestingConfig(Config):
    """Configuración para entorno de testing"""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
