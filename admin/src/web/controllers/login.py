# admin/src/web/controllers/login.py
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from core.services.auth_service import authenticate

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    '''Maneja el inicio de sesión de usuarios'''
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = authenticate(request.form["email"], request.form["password"])
        if user:
            # Guardar solo el id del usuario en la sesión (no el objeto SQLAlchemy)
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            flash("Usuario o clave incorrectos.", "error")
            return render_template("login.html", email=request.form["email"], pw=request.form["password"])
