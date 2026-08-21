from tests.conftest import auth_headers, register_user, unique_email


def test_register_creates_user_and_returns_token(client):
    token, user = register_user(client)
    assert token
    assert user["email"]


def test_register_duplicate_email_fails(client):
    email = unique_email()
    register_user(client, email=email)
    resp = client.post(
        "/api/v1/auth/register", json={"email": email, "name": "Dup", "password": "password123"}
    )
    assert resp.status_code == 409


def test_login_with_correct_credentials(client):
    email = unique_email()
    register_user(client, email=email, password="password123")
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_with_wrong_password_fails(client):
    email = unique_email()
    register_user(client, email=email, password="password123")
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    token, user = register_user(client)
    resp = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == user["id"]
