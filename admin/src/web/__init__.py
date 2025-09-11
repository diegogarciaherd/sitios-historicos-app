from flask import Flask
from src.web.handlers import error


def create_app(env="development", static_folder=""): 
  app = Flask(__name__)

  @app.route('/')
  def home():
    return "¡Hola mundo!"

  app.register_error_handler(404, error.not_found)

  return app
