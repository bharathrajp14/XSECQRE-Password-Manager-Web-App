# XSECQRE – Secure Password Manager

XSECQRE is a web-based **password manager** built with **Python, Flask, and SQLite**. It allows users to sign up, log in, and securely store, view, update, and delete credentials. Each user can only access their own records, account passwords are hashed, and saved site credentials are encrypted at rest.

## Features

- User authentication with Flask-Login.
- Password hashing using Werkzeug’s current password-hashing defaults.
- Encrypted storage for saved site credentials using an application secret.
- Ownership checks on every credential read, update, and delete operation.
- POST-only credential deletion.
- Responsive Bootstrap 5 interface.

## Installation

```bash
git clone https://github.com/yourusername/xsecqre-password-manager.git
cd xsecqre-password-manager
python -m pip install -r requirements.txt
```

Set a stable secret before running a deployed instance. The application creates a local `instance/secret.key` automatically for development, but a hosted deployment should provide a persistent value instead:

```bash
export SECRET_KEY="replace-with-a-long-random-value"
export PORT=8080
python app.py
```

If `DATABASE_URL` is not set, the application uses `instance/data.db`. Existing plaintext credential rows are encrypted once at startup using the configured application secret. **Back up the database and preserve `SECRET_KEY` before deploying or rotating infrastructure.**

The hosted deployment is available at [xsecqre.onrender.com](https://xsecqre.onrender.com/).
