from flask import Flask, request
from flask import render_template, session, redirect, url_for
from core import database
from web.handlers import error
from web.controllers.login import login_bp
from web.controllers.logout import logout_bp
from web.controllers.sites import sites_bp
from web.controllers.feature_flags import feature_flags_bp
from flask_session import Session
from core import database
from web.config import config
from core.services.auth_service import check_flags

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    Session(app)

    # Initialize database
    database.init_app(app)

    # Register blueprints
    app.register_blueprint(sites_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(feature_flags_bp)

    @app.route('/')
    def home():
        return render_template("home.html", logged_user=session['user_id'] if 'user_id' in session else None)
    
    @app.route('/under-maintenance')
    def under_maintenance():
        return render_template("under_maintenance.html", logged_user=session['user_id'] if 'user_id' in session else None)
    
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    # Register commands
    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()
    
    @app.cli.command("seed-db")
    def seed_db():
        database.seed_db()

    @app.route('/mantenimiento')
    def mantenimiento():
        return render_template("mantenimiento.html", logged_user=session['user_id'] if 'user_id' in session else None)
    
    @app.before_request
    def before_request():
        if check_flags(session.get('user_id')) and request.endpoint not in ['mantenimiento', 'login.login', 'static', 'logout.logout']:
            return redirect('/mantenimiento')
        if not check_flags(None) and request.endpoint == 'mantenimiento':
            return redirect(url_for('home'))
        

    return app
