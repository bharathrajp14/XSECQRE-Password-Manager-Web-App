import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def _cipher():
    secret = str(current_app.config["SECRET_KEY"]).encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt_secret(value):
    return _cipher().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_secret(value):
    return _cipher().decrypt(value.encode("ascii")).decode("utf-8")


def is_encrypted(value):
    try:
        decrypt_secret(value)
        return True
    except (InvalidToken, ValueError, TypeError):
        return False
