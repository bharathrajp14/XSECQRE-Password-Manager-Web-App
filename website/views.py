from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .crypto import encrypt_secret
from .models import Password

views = Blueprint("views", __name__)


def valid_optional_url(value):
    if not value:
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route("/passwords")
@login_required
def passwords():
    user_passwords = Password.query.filter_by(user_id=current_user.id).order_by(Password.created_at.desc()).all()
    return render_template("password_manager.html", passwords=user_passwords)


@views.route("/passwords/add", methods=["POST"])
@login_required
def add_password():
    site_name = (request.form.get("site_name") or "").strip()
    site_url = (request.form.get("site_url") or "").strip()
    site_password = request.form.get("site_password") or ""

    if not site_name or not site_password:
        flash("Site name and password are required.", "error")
    elif not valid_optional_url(site_url):
        flash("Site URL must start with http:// or https://.", "error")
    else:
        db.session.add(
            Password(
                site_name=site_name,
                site_url=site_url or None,
                site_password=encrypt_secret(site_password),
                user_id=current_user.id,
            )
        )
        db.session.commit()
        flash("Password added successfully.", "success")
    return redirect(url_for("views.passwords"))


@views.route("/passwords/edit/<int:id>", methods=["POST"])
@login_required
def edit_password(id):
    password_entry = Password.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    site_name = (request.form.get("site_name") or "").strip()
    site_url = (request.form.get("site_url") or "").strip()
    site_password = request.form.get("site_password") or ""

    if not site_name or not site_password:
        flash("Site name and password are required.", "error")
    elif not valid_optional_url(site_url):
        flash("Site URL must start with http:// or https://.", "error")
    else:
        password_entry.site_name = site_name
        password_entry.site_url = site_url or None
        password_entry.site_password = encrypt_secret(site_password)
        db.session.commit()
        flash("Password updated successfully.", "success")
    return redirect(url_for("views.passwords"))


@views.route("/passwords/delete/<int:id>", methods=["POST"])
@login_required
def delete_password(id):
    password_entry = Password.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(password_entry)
    db.session.commit()
    flash("Password deleted successfully.", "success")
    return redirect(url_for("views.passwords"))
