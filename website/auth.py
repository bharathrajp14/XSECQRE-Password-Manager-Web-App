from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        username = (request.form.get("user") or "").strip()
        password = request.form.get("password") or ""

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif username:
            user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash("Logged in successfully!", category="success")
            return redirect(url_for("views.passwords"))

        flash("Invalid login details.", category="error")

    return render_template("login.html")


@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = (request.form.get("user") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password1 = request.form.get("password") or ""
        password2 = request.form.get("password1") or ""

        if not username or not email or not password1 or not password2:
            flash("All fields are required.", category="error")
        elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Enter a valid email address.", category="error")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists.", category="error")
        elif User.query.filter_by(username=username).first():
            flash("Username already exists.", category="error")
        elif password1 != password2:
            flash("Passwords do not match.", category="error")
        elif len(password1) < 8:
            flash("Password must be at least 8 characters long.", category="error")
        elif len(username) < 2:
            flash("Username must be at least 2 characters long.", category="error")
        else:
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password1),
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created successfully!", category="success")
            return redirect(url_for("views.passwords"))

    return render_template("sign_up.html")


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("auth.login"))
