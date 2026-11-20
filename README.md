# Secure Support Ticket API

A role-based support ticket API built with **FastAPI**, **SQLModel**, and **JWT authentication**. It supports three roles:

- `user` — creates and views their own support tickets.
- `staff` — views tickets across users and handles ticket progress.
- `admin` — has staff-level ticket access and can manage account roles through a trusted local script.

## Features

- User registration and login
- Password hashing (Argon2; plaintext passwords are not stored)
- JWT access-token authentication using HS256
- Role-based authorization (`user`, `staff`, `admin`)
- Ticket ownership enforcement
- Ticket status workflow: `open`, `in_progress`, `resolved`
- Local role-promotion command for trusted administrators

## Requirements

- Python 3.12 or a compatible Python version
- pip
- Git
- SQLite for the default local setup, or a database supported by the configured SQLModel/SQLAlchemy driver

## 1. Clone the repository

```bash
git clone https://github.com/SakshiKhatiwada/Secure-Support-Ticket-API.git
cd Secure-Support-Ticket-API
```

Run all commands below from the project root — the directory containing `app/` and `scripts/`.

## 2. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file in the project root. Do not commit this file.

Example for a local SQLite database:

```env
DB_URL=sqlite:///../support_tickets.db
SIGNATURE_KEY=replace-this-with-a-cryptographically-random-secret
ALGORITHM="HS256"
TOKEN_EXPIRY_TIME=30
INITIAL_ADMIN_PASSWORD=replace-with-your-password
```

`INITIAL_ADMIN_PASSWORD` is optional and intended for `create_admin.py` file for manual initial admin creation step.

### Generate a secure JWT secret

Generate a random secret instead of writing your own:

```bash
openssl rand -hex 32
```

Copy the output into `SIGNATURE_KEY` in `.env`.

Do not:
- commit `.env` or share its contents;
- hard-code the secret in source code;
- use a predictable value such as `secret`, `password`, or `development-key` outside disposable local tests.

The API uses HS256, so the same secret is used to sign and verify access tokens. Keep it private.

## 5. Database configuration

### SQLite (default local development setup)

```env
DB_URL=sqlite:///../support_tickets.db
```

## 6. Start the API

From the repository root, with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

or 

```bash
fastapi dev
```

The local API should be available at:

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`


## 7. Create demo accounts and assign roles

### Step 1 — Register accounts

Use the registration endpoint exposed in Swagger UI (`POST /auth/register`) to create accounts. Registration assigns the default role:

```text
user
```

Create separate accounts for the demo, for example:

| Username | Intended demo role |
|---|---|
| `demo_user` | `user` |
| `demo_staff` | `staff` |
| `demo_admin` | `admin` |

Usernames are unique and should be strong, non-production demo passwords. The API hashes each password before storing it.

### Step 2 — Promote accounts using the trusted local script

Role changes are performed locally by a trusted operator, not by accepting a role value from public registration input.

Run the promotion command from the repository root:

```bash
python -m scripts.promote_user demo_staff staff
```

Promote the admin account with the additional confirmation flag:

```bash
python -m scripts.promote_user demo_admin admin --confirm
```

The supported role values are exactly:

```text
user
staff
admin
```

The target account must already exist. The script validates the requested role and updates the existing user's role in the database. This script is restricted to trusted local operators.

### Step 3 — Log in and obtain access tokens

Log in separately as each demo account using the login endpoint exposed by the application (`POST /auth/login`). Use the returned access token as a Bearer token in Swagger UI:

```text
Authorization: Bearer <access_token>
```

Use the `/auth/me` endpoint, to inspect the authenticated account's public profile and current role.

## 8. Permission matrix

The following describes the intended authorization policy implemented by the role checks and ticket ownership rules. A user must be authenticated before any protected operation.

| Endpoint | `user` | `staff` | `admin` |
|---|:---:|:---:|:---:|
| POST /tickets |Create own |Create own |Create own|
| GET /tickets |Own only| All| All|
| GET /tickets/{id}| Own only| Any| Any|
| PUT /tickets/{id} |Own + open| Own + open| Own + open|
| PATCH /tickets/{id}/status| Denied| Any| Any|
| DELETE /tickets/{id} |Denied |Denied |Any|
| GET /admin/users| Denied |Denied |Allowed|

**Ownership rule:** a regular user's ticket access is scoped to the authenticated user's database ID. The API derives `owner_id` from the authenticated user, not trust an owner ID supplied by the client.

**Ticket lifecycle:**

- `open` — newly submitted ticket; the server sets this initial status.
- `in_progress` — staff is investigating the issue.
- `resolved` — the issue has been fixed.

The client is not allowed to choose an arbitrary initial status when creating a ticket. Role checks is applied to status-changing and other staff-only actions.

## 9. Important authentication and security notes

- Passwords are stored as password hashes, not plaintext.
- JWT access tokens are signed with HS256 and sent using the Bearer authentication scheme.
- The token identifies the account; the application retrieves the current user from the database when authenticating requests. Consequently, authorization uses the account's current database role rather than relying on a role claim as the sole source of truth.
- Registration creates a regular `user` account. Privileged roles are assigned through the trusted local role-management script.
- `hashed_password` is never returned in API responses.

### Out of scope

This project implements **access-token authentication only**. The following are intentionally out of scope:

- **Refresh tokens:** there is no refresh-token flow for obtaining a new access token without logging in again.
- **Token revocation:** there is no token denylist or server-side revocation mechanism for invalidating an already-issued access token before its expiry.

A role change affects authorization on subsequent requests because the current role is loaded from the database. This is not the same as revoking the token: the token itself remains cryptographically valid until it expires, but the user's permissions are evaluated using the updated database role.

## 10. Project structure

The relevant structure is expected to resemble:

```text
Secure-Support-Ticket-API/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── utils/
│   ├── config.py
│   └── data.py
├── scripts/
│   ├── __init__.py
│   └── promote_user.py
├── tests/
├── .env
├── .env.example
├── .gitignore
├── (db file will be created here)
├── README.md
└── requirements.txt
```
Additionally,

```text
├── models/
│   ├── ticket.py
│   ├── token.py
│   └── user.py
```

```text
├── routers/
│   ├── admin.py
│   ├── authentication.py
│   └── tickets.py
```

```text
├── utisl/
│   ├── auth.py
│   ├── create_admin.py
│   ├── db.py
│   ├── normalization.py
│   ├── passwords.py
│   └── tokens.py
```

## 11. Running tests

The project uses pytest, run the test suite from the repository root:

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

Keep test credentials and test database configuration separate from production settings.