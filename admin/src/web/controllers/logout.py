from flask import Blueprint, session
from flask import redirect, url_for

logout_bp = Blueprint("logout", __name__)

@logout_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    print("entre")
    return redirect(url_for("home"))
