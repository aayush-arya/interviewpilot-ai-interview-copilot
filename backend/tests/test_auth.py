def test_register_login_me(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "Passw0rd1", "full_name": "Alice"},
    )
    assert r.status_code == 201, r.text

    # duplicate email rejected
    assert client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "Passw0rd1", "full_name": "Alice"},
    ).status_code == 409

    tokens = client.post(
        "/api/v1/auth/login", json={"email": "a@b.com", "password": "Passw0rd1"}
    ).json()
    assert "access_token" in tokens

    me = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "a@b.com"
    assert me.json()["xp"] >= 5  # login XP awarded


def test_weak_password_rejected(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "w@b.com", "password": "short", "full_name": "W"},
    )
    assert r.status_code == 422


def test_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "c@b.com", "password": "Passw0rd1", "full_name": "C"},
    )
    r = client.post("/api/v1/auth/login", json={"email": "c@b.com", "password": "Wrong0000"})
    assert r.status_code == 401


def test_refresh_token_type_enforced(client, auth_headers):
    access = auth_headers["Authorization"].split()[1]
    # access token must not work as refresh token
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": access}).status_code == 401


def test_protected_route_requires_auth(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_forgot_password_no_enumeration(client):
    r = client.post("/api/v1/auth/forgot-password", json={"email": "ghost@nowhere.com"})
    assert r.status_code == 202


def test_admin_gate(client, auth_headers):
    assert client.get("/api/v1/admin/stats", headers=auth_headers).status_code == 403
