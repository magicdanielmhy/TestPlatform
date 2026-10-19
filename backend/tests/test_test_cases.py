def _payload(**overrides):
    payload = {
        "name": "get index",
        "method": "GET",
        "url": "http://example.com/",
        "assertions": [{"type": "status", "expected": 200}],
    }
    payload.update(overrides)
    return payload


def test_create_and_get_case(client, auth_headers):
    response = client.post(
        "/api/test-cases", json=_payload(), headers=auth_headers
    )
    assert response.status_code == 201
    created = response.json()
    assert created["id"]

    response = client.get(f"/api/test-cases/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "get index"


def test_create_missing_required_field(client, auth_headers):
    response = client.post(
        "/api/test-cases", json={"name": "no url"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_list_cases(client, auth_headers):
    client.post("/api/test-cases", json=_payload(name="a"), headers=auth_headers)
    client.post("/api/test-cases", json=_payload(name="b"), headers=auth_headers)
    response = client.get("/api/test-cases", headers=auth_headers)
    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    assert {"a", "b"} <= names


def test_update_case(client, auth_headers):
    created = client.post("/api/test-cases", json=_payload(), headers=auth_headers).json()
    response = client.put(
        f"/api/test-cases/{created['id']}",
        json={"name": "renamed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "renamed"


def test_delete_case(client, auth_headers):
    created = client.post("/api/test-cases", json=_payload(), headers=auth_headers).json()
    response = client.delete(
        f"/api/test-cases/{created['id']}", headers=auth_headers
    )
    assert response.status_code == 204
    response = client.get(f"/api/test-cases/{created['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_get_not_found(client, auth_headers):
    response = client.get("/api/test-cases/99999", headers=auth_headers)
    assert response.status_code == 404
