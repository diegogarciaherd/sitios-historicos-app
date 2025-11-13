# admin/src/web/__init__.py
from flask import Flask, render_template, jsonify, url_for, redirect, request, g
from web.handlers import error
from web.controllers.login import login_bp
from web.controllers.logout import logout_bp
from web.controllers.adminpanel import adminpanel_bp
from core.services.bcrypt import bcrypt
from web.controllers.tags import tags_bp
from web.controllers.sites import sites_bp
from web.controllers.feature_flags import feature_flags_bp
from flask_session import Session
from core import database
from web.config import config
from core.services.auth_service import check_flags
from core.models.feature_flags import FeatureFlag
from core.seeds_roles import run as seed_roles_run
from web.api.sites import sites_api_bp
from web.api.auth import auth_api_bp
from flask_jwt_extended import JWTManager
from web.controllers.reviews import reviews_bp



# Auth helpers (roles/permisos)
from core.services.auth_roles import load_user, inject_template_helpers

def create_app(env="development", static_folder="../../static"):
    ''' Crea y configura la aplicación Flask '''
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    Session(app)

    jwt = JWTManager(app)

    # DB
    database.init_app(app)
    # Initialize bcrypt
    bcrypt.init_app(app)

    # Auth: cargar usuario y helpers para Jinja en cada request
    app.before_request(load_user)
    app.context_processor(inject_template_helpers)

    # Blueprints
    app.register_blueprint(sites_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(adminpanel_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(feature_flags_bp)
    # API blueprints
    app.register_blueprint(sites_api_bp)
    app.register_blueprint(auth_api_bp)
    app.register_blueprint(reviews_bp)

    # Rutas mínimas
    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.route("/health/db")
    def health_db():
        ok = database.ping_db()
        return jsonify(status="ok" if ok else "down"), (200 if ok else 500)

    # Errores
    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.server_error)

    # Comandos
    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        database.seed_db()

    @app.cli.command("seed-roles")
    def seed_roles():
        seed_roles_run()


    @app.route('/mantenimiento')
    def mantenimiento():
        message = database.db.session.query(FeatureFlag).filter(FeatureFlag.name=="Sistema administrativo").first().message
        return render_template("mantenimiento.html", message=message if message else "")

    @app.before_request
    def before_request():
        if check_flags(g.user) and request.endpoint not in ['mantenimiento', 'login.login', 'static', 'logout.logout']:
            return redirect('/mantenimiento')
        if not check_flags(None) and request.endpoint == 'mantenimiento':
            return redirect(url_for('home'))
        

    return app
