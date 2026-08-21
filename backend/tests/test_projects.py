from tests.conftest import auth_headers, register_user


def setup_workspace(client, token):
    resp = client.post("/api/v1/workspaces", json={"name": "Acme"}, headers=auth_headers(token))
    return resp.json()


def test_create_project(client):
    token, _ = register_user(client)
    ws = setup_workspace(client, token)
    resp = client.post(
        "/api/v1/projects",
        json={"workspace_id": ws["id"], "name": "Website Redesign", "description": "Q3 redesign"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Website Redesign"
    assert data["status"] == "PLANNING"
    assert data["progress"] == 0.0


def test_update_project_status(client):
    token, _ = register_user(client)
    ws = setup_workspace(client, token)
    project = client.post(
        "/api/v1/projects", json={"workspace_id": ws["id"], "name": "P1"}, headers=auth_headers(token)
    ).json()

    resp = client.patch(
        f"/api/v1/projects/{project['id']}", json={"status": "ACTIVE"}, headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACTIVE"


def test_delete_project(client):
    token, _ = register_user(client)
    ws = setup_workspace(client, token)
    project = client.post(
        "/api/v1/projects", json={"workspace_id": ws["id"], "name": "P1"}, headers=auth_headers(token)
    ).json()

    resp = client.delete(f"/api/v1/projects/{project['id']}", headers=auth_headers(token))
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers(token))
    assert resp.status_code == 404


def test_list_projects_scoped_to_workspace(client):
    token, _ = register_user(client)
    ws1 = setup_workspace(client, token)
    ws2 = client.post("/api/v1/workspaces", json={"name": "Other"}, headers=auth_headers(token)).json()
    client.post("/api/v1/projects", json={"workspace_id": ws1["id"], "name": "In WS1"}, headers=auth_headers(token))
    client.post("/api/v1/projects", json={"workspace_id": ws2["id"], "name": "In WS2"}, headers=auth_headers(token))

    resp = client.get(f"/api/v1/projects?workspace_id={ws1['id']}", headers=auth_headers(token))
    names = [p["name"] for p in resp.json()]
    assert names == ["In WS1"]
