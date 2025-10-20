# admin/src/web/controllers/login.py
from flask import Blueprint, redirect, url_for, render_template, request, session
from core.services.auth_service import authenticate
from core.models.user import create_user
from core.models.userrole import UserRole

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = authenticate(request.form["email"], request.form["password"])
        if user:
            # Guardar solo el id del usuario en la sesión (no el objeto SQLAlchemy)
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Usuario o clave incorrectos.")
