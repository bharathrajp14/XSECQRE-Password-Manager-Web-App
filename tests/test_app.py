import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from website import create_app, db
from website.crypto import decrypt_secret
from website.models import Password


def test_credentials_are_encrypted_and_delete_is_post_only(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        }
    )
    client = app.test_client()

    signup = client.post(
        "/sign_up",
        data={
            "user": "alice",
            "email": "alice@example.com",
            "password": "correct horse battery staple",
            "password1": "correct horse battery staple",
        },
        follow_redirects=True,
    )
    assert signup.status_code == 200

    add = client.post(
        "/passwords/add",
        data={
            "site_name": "Example",
            "site_url": "https://example.com",
            "site_password": "super-secret",
        },
        follow_redirects=True,
    )
    assert add.status_code == 200
    assert b"super-secret" not in add.data

    with app.app_context():
        credential = db.session.query(Password).one()
        assert credential.site_password != "super-secret"
        assert decrypt_secret(credential.site_password) == "super-secret"
        credential_id = credential.id

    assert client.get(f"/passwords/delete/{credential_id}").status_code == 405
    deleted = client.post(f"/passwords/delete/{credential_id}", follow_redirects=True)
    assert deleted.status_code == 200
    with app.app_context():
        assert db.session.get(Password, credential_id) is None
