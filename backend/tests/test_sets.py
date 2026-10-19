def _case(client, auth_headers, name="case"):
    return client.post(
        "/api/test-cases",
        json={"name": name, "method": "GET", "url": "http://example.com/"},
        headers=auth_headers,
    ).json()


def _set(client, auth_headers, name="smoke"):
    return client.post(
        "/api/test-case-sets", json={"name": name}, headers=auth_headers
    ).json()


def test_create_set(client, auth_headers):
    response = client.post(
        "/api/test-case-sets", json={"name": "smoke"}, headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["member_count"] == 0


def test_add_and_remove_member(client, auth_headers):
    case = _case(client, auth_headers)
    s = _set(client, auth_headers)

    response = client.post(
        f"/api/test-case-sets/{s['id']}/members",
        json={"test_case_id": case["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 201

    detail = client.get(f"/api/test-case-sets/{s['id']}", headers=auth_headers).json()
    assert [m["id"] for m in detail["members"]] == [case["id"]]

    response = client.delete(
        f"/api/test-case-sets/{s['id']}/members/{case['id']}", headers=auth_headers
    )
    assert response.status_code == 204

    detail = client.get(f"/api/test-case-sets/{s['id']}", headers=auth_headers).json()
    assert detail["members"] == []


def test_remove_member_keeps_case(client, auth_headers):
    case = _case(client, auth_headers)
    s = _set(client, auth_headers)
    client.post(
        f"/api/test-case-sets/{s['id']}/members",
        json={"test_case_id": case["id"]},
        headers=auth_headers,
    )
    client.delete(
        f"/api/test-case-sets/{s['id']}/members/{case['id']}", headers=auth_headers
    )
    response = client.get(f"/api/test-cases/{case['id']}", headers=auth_headers)
    assert response.status_code == 200


def test_delete_set_keeps_cases(client, auth_headers):
    case = _case(client, auth_headers)
    s = _set(client, auth_headers)
    client.post(
        f"/api/test-case-sets/{s['id']}/members",
        json={"test_case_id": case["id"]},
        headers=auth_headers,
    )
    response = client.delete(f"/api/test-case-sets/{s['id']}", headers=auth_headers)
    assert response.status_code == 204
    response = client.get(f"/api/test-cases/{case['id']}", headers=auth_headers)
    assert response.status_code == 200
