from tests.conftest import auth_headers, register_user


def setup_task(client, token):
    ws = client.post("/api/v1/workspaces", json={"name": "Acme"}, headers=auth_headers(token)).json()
    project = client.post(
        "/api/v1/projects", json={"workspace_id": ws["id"], "name": "P1"}, headers=auth_headers(token)
    ).json()
    task = client.post(
        "/api/v1/tasks", json={"project_id": project["id"], "title": "T1"}, headers=auth_headers(token)
    ).json()
    return ws, project, task


def test_add_comment_to_task(client):
    token, _ = register_user(client)
    _, _, task = setup_task(client, token)

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/comments", json={"body": "Looks good to me"}, headers=auth_headers(token)
    )
    assert resp.status_code == 201
    assert resp.json()["body"] == "Looks good to me"


def test_list_comments_ordered(client):
    token, _ = register_user(client)
    _, _, task = setup_task(client, token)
    client.post(f"/api/v1/tasks/{task['id']}/comments", json={"body": "first"}, headers=auth_headers(token))
    client.post(f"/api/v1/tasks/{task['id']}/comments", json={"body": "second"}, headers=auth_headers(token))

    resp = client.get(f"/api/v1/tasks/{task['id']}/comments", headers=auth_headers(token))
    bodies = [c["body"] for c in resp.json()]
    assert bodies == ["first", "second"]


def test_non_member_cannot_comment(client):
    token_a, _ = register_user(client)
    token_b, _ = register_user(client)
    _, _, task = setup_task(client, token_a)

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/comments", json={"body": "sneaky"}, headers=auth_headers(token_b)
    )
    assert resp.status_code == 403


def test_comment_appears_in_task_activity(client):
    token, _ = register_user(client)
    _, _, task = setup_task(client, token)
    client.post(f"/api/v1/tasks/{task['id']}/comments", json={"body": "note"}, headers=auth_headers(token))

    resp = client.get("/api/v1/activity", headers=auth_headers(token))
    actions = [a["action"] for a in resp.json()]
    assert "COMMENT_ADDED" in actions
