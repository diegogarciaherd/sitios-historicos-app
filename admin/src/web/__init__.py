from flask import Flask, session
from flask import render_template
from src.web.handlers import error
from web.controllers.login import login_bp
from web.controllers.logout import logout_bp
from flask_session import Session
from src.core import database
from src.web.config import config

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    
    database.init_db(app)

    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.register_blueprint(login_bp)
    app.register_blueprint(logout_bp)

    # resetea siempre para probar
    database.reset_db()

    @app.route('/')
    def home():
  
        return render_template("home.html", logged_user=session.get("user_id"))
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    return app
