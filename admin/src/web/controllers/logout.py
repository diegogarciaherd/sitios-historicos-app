from flask import Blueprint, session
from flask import redirect, url_for
from web.decorators.loginrequired import login_required

logout_bp = Blueprint("logout", __name__)

@logout_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Controlador que maneja la logica de cierre de sesion.
    """
    if session:
        session.clear()
    return redirect(url_for("home"))
