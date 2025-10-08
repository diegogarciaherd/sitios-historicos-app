# src/web/__init__.py
<<<<<<< HEAD
from flask import Flask, render_template, jsonify
=======
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)
from flask_session import Session

from core import database
from web.handlers import error
from web.config import config

from web.controllers.login import login_bp
from web.controllers.logout import logout_bp
from web.controllers.sites import sites_bp

<<<<<<< HEAD
# helpers de auth/roles
from core.services.auth_roles import inject_template_helpers # can(), has_role(), current_user()
from core.services.auth_roles import load_user # setea g.user

=======
# helpers de auth/roles:
from core.services.auth_service import load_user
from core.services.auth_roles import can as _can, get_logged_user
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config[env])
    Session(app)

    # DB
    database.init_app(app)

<<<<<<< HEAD
    # Auth: cargar user y helpers Jinja
    app.before_request(load_user)
    app.context_processor(inject_template_helpers)
=======
    # Cargar usuario en cada request
    app.before_request(load_user)

    # Inyectar helpers a Jinja: logged_user y can('perm.code')
    @app.context_processor
    def inject_auth_helpers():
        user = get_logged_user()
        return {
            "logged_user": user,
            "can": (lambda code: _can(user, code)),
        }
>>>>>>> 1bae15a (agregue decoradores para permisos y bloques de chequeo en las vistas)

    # Blueprints
    app.register_blueprint(sites_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(login_bp)

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

    return app
