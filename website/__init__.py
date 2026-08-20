import os
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def _load_secret_key(app):
    configured = os.environ.get("SECRET_KEY")
    if configured:
        return configured

    key_path = os.path.join(app.instance_path, "secret.key")
    try:
        with open(key_path, "r", encoding="utf-8") as handle:
            return handle.read().strip()
    except FileNotFoundError:
        generated = secrets.token_urlsafe(32)
        with open(key_path, "w", encoding="utf-8") as handle:
            handle.write(generated)
        return generated


def _migrate_legacy_credentials():
    from .crypto import encrypt_secret, is_encrypted
    from .models import Password

    changed = False
    for credential in Password.query.all():
        if not is_encrypted(credential.site_password):
            credential.site_password = encrypt_secret(credential.site_password)
            changed = True
    if changed:
        db.session.commit()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        database_url = f"sqlite:///{os.path.join(app.instance_path, 'data.db')}"

    app.config.from_mapping(
        SECRET_KEY=_load_secret_key(app),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from .auth import auth
    from .models import User
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    with app.app_context():
        db.create_all()
        _migrate_legacy_credentials()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    return app
