def _create(client, auth_headers, url, assertions):
    return client.post(
        "/api/test-cases",
        json={
            "name": "exec case",
            "method": "GET",
            "url": url,
            "assertions": assertions,
        },
        headers=auth_headers,
    ).json()


def test_execute_pass(client, auth_headers, stub_server):
    case = _create(
        client, auth_headers, f"{stub_server}/success", [{"type": "status", "expected": 200}]
    )
    response = client.post(f"/api/test-cases/{case['id']}/execute", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "pass"
    assert result["response_status"] == 200


def test_execute_fail_on_assertion(client, auth_headers, stub_server):
    case = _create(
        client, auth_headers, f"{stub_server}/success", [{"type": "status", "expected": 201}]
    )
    result = client.post(
        f"/api/test-cases/{case['id']}/execute", headers=auth_headers
    ).json()
    assert result["status"] == "fail"


def test_execute_body_contains(client, auth_headers, stub_server):
    case = _create(
        client,
        auth_headers,
        f"{stub_server}/success",
        [{"type": "body", "expected": "pon", "operator": "contains"}],
    )
    result = client.post(
        f"/api/test-cases/{case['id']}/execute", headers=auth_headers
    ).json()
    assert result["status"] == "pass"


def test_execute_error_unreachable(client, auth_headers):
    case = _create(
        client, auth_headers, "http://127.0.0.1:1/nope", [{"type": "status", "expected": 200}]
    )
    result = client.post(
        f"/api/test-cases/{case['id']}/execute", headers=auth_headers
    ).json()
    assert result["status"] == "error"


def test_execute_set_and_summary(client, auth_headers, stub_server):
    a = _create(
        client, auth_headers, f"{stub_server}/success", [{"type": "status", "expected": 200}]
    )
    b = _create(
        client, auth_headers, f"{stub_server}/success", [{"type": "status", "expected": 201}]
    )
    s = client.post(
        "/api/test-case-sets", json={"name": "batch"}, headers=auth_headers
    ).json()
    for case in (a, b):
        client.post(
            f"/api/test-case-sets/{s['id']}/members",
            json={"test_case_id": case["id"]},
            headers=auth_headers,
        )

    result = client.post(
        f"/api/test-case-sets/{s['id']}/execute", headers=auth_headers
    ).json()
    assert result["total"] == 2
    assert result["passed"] == 1
    assert result["failed"] == 1
    assert result["errors"] == 0


def test_view_execution_history(client, auth_headers, stub_server):
    case = _create(
        client, auth_headers, f"{stub_server}/success", [{"type": "status", "expected": 200}]
    )
    client.post(f"/api/test-cases/{case['id']}/execute", headers=auth_headers)
    response = client.get(f"/api/test-cases/{case['id']}/executions", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["status"] == "pass"
