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

    DB_USER = environ["DB_USER"]
    DB_PASSWORD = environ["DB_PASSWORD"]
    DB_HOST = environ["DB_HOST"]
    DB_PORT = environ["DB_PORT"]
    DB_NAME = environ["DB_NAME"]
    DB_SCHEME = environ["DB_SCHEME"]
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