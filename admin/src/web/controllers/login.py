# admin/src/web/controllers/login.py
from flask import Blueprint, redirect, url_for, render_template, request, session
from core.services.auth_service import authenticate

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = authenticate(request.form["email"], request.form["password"])
    if user:
        session["user_id"] = user.email  # usado por load_user()
        return redirect(url_for("home"))
    return render_template("login.html", error="Usuario o clave incorrectos.")
