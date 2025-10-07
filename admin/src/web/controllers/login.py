from flask import Blueprint, redirect, url_for
from flask import render_template
from flask import request, session
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
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["user_role"] = user.role
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Usuario o clave incorrectos.")
