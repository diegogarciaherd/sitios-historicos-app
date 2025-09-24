from flask import Blueprint, redirect, url_for
from flask import render_template
from flask import request, session

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        session["user_id"] = request.form["email"]
        return redirect(url_for("home", logged_user=session["user_id"]))
