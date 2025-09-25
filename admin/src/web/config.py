from os import environ

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

    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "grupo45"
    DB_SCHEME = "postgresql+psycopg2"
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