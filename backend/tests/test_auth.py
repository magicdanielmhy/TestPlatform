def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


def test_protected_without_token(client):
    response = client.get("/api/test-cases")
    assert response.status_code == 401


def test_protected_with_invalid_token(client):
    response = client.get(
        "/api/test-cases", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
