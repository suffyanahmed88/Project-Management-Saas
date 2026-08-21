from tests.conftest import auth_headers, register_user


def create_workspace(client, token, name="Acme Inc"):
    resp = client.post("/api/v1/workspaces", json={"name": name}, headers=auth_headers(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_user_cannot_see_other_users_workspace(client):
    token_a, _ = register_user(client)
    token_b, _ = register_user(client)

    ws_a = create_workspace(client, token_a)

    resp = client.get("/api/v1/workspaces", headers=auth_headers(token_b))
    ids = [w["id"] for w in resp.json()]
    assert ws_a["id"] not in ids


def test_non_member_cannot_create_project_in_workspace(client):
    token_a, _ = register_user(client)
    token_b, _ = register_user(client)
    ws_a = create_workspace(client, token_a)

    resp = client.post(
        "/api/v1/projects",
        json={"workspace_id": ws_a["id"], "name": "Secret Project"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 403


def test_non_member_cannot_view_project(client):
    token_a, _ = register_user(client)
    token_b, _ = register_user(client)
    ws_a = create_workspace(client, token_a)
    proj = client.post(
        "/api/v1/projects",
        json={"workspace_id": ws_a["id"], "name": "P1"},
        headers=auth_headers(token_a),
    ).json()

    resp = client.get(f"/api/v1/projects/{proj['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 403


def test_workspace_created_makes_creator_owner(client):
    token, _ = register_user(client)
    ws = create_workspace(client, token)
    assert ws["my_role"] == "OWNER"
