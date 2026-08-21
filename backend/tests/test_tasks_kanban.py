from tests.conftest import auth_headers, register_user


def setup_project(client, token):
    ws = client.post("/api/v1/workspaces", json={"name": "Acme"}, headers=auth_headers(token)).json()
    project = client.post(
        "/api/v1/projects", json={"workspace_id": ws["id"], "name": "P1"}, headers=auth_headers(token)
    ).json()
    return ws, project


def test_create_task_defaults_to_backlog(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    resp = client.post(
        "/api/v1/tasks",
        json={"project_id": project["id"], "title": "Design landing page"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "BACKLOG"
    assert resp.json()["position"] == 0


def test_move_task_between_columns_persists(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token)
    ).json()

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/move",
        json={"status": "IN_PROGRESS", "position": 0},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"

    fetched = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token))
    assert fetched.json()["status"] == "IN_PROGRESS"


def test_task_position_increments_within_column(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    t1 = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1", "status": "TODO"},
        headers=auth_headers(token),
    ).json()
    t2 = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T2", "status": "TODO"},
        headers=auth_headers(token),
    ).json()
    assert t1["position"] == 0
    assert t2["position"] == 1


def test_update_task_fields(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token)
    ).json()

    resp = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"priority": "URGENT", "labels": ["bug", "frontend"]},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["priority"] == "URGENT"
    assert set(body["labels"]) == {"bug", "frontend"}


def test_completing_task_marks_done(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token)
    ).json()

    resp = client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "DONE"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "DONE"

    project_resp = client.get(f"/api/v1/projects/{project['id']}", headers=auth_headers(token))
    assert project_resp.json()["progress"] == 100.0


def test_delete_task(client):
    token, _ = register_user(client)
    _, project = setup_project(client, token)
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token)
    ).json()

    resp = client.delete(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token))
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers(token))
    assert resp.status_code == 404


def test_non_member_cannot_move_task(client):
    token_a, _ = register_user(client)
    token_b, _ = register_user(client)
    _, project = setup_project(client, token_a)
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token_a)
    ).json()

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/move",
        json={"status": "DONE", "position": 0},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 403
