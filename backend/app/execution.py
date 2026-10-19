import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from .config import settings
from .models import ExecutionResult, TestCase


def new_run_id() -> int:
    return int(time.time() * 1000)


def _check_assertion(assertion: dict, status_code: int, body: str) -> dict:
    a_type = assertion.get("type")
    expected = assertion.get("expected")
    operator = assertion.get("operator", "contains")

    if a_type == "status":
        actual: str | int = status_code
        passed = int(expected) == status_code
    else:
        actual = body
        if operator == "equals":
            passed = body == expected
        else:
            passed = expected in body

    return {
        "type": a_type,
        "expected": expected,
        "operator": operator,
        "actual": actual,
        "passed": passed,
    }


def execute_case(test_case: TestCase, db: Session, set_run_id: int | None = None) -> ExecutionResult:
    result = ExecutionResult(
        test_case_id=test_case.id,
        set_run_id=set_run_id,
        status="pass",
        request_snapshot={
            "method": test_case.method,
            "url": test_case.url,
            "headers": test_case.headers,
            "body": test_case.body,
        },
    )
    result.started_at = datetime.now(timezone.utc)

    try:
        content = test_case.body.encode("utf-8") if test_case.body else None
        response = httpx.request(
            test_case.method,
            test_case.url,
            headers=test_case.headers or None,
            content=content,
            timeout=settings.EXECUTE_TIMEOUT,
        )
        result.response_status = response.status_code
        result.response_body = response.text
        assertion_results = [
            _check_assertion(a, response.status_code, response.text)
            for a in (test_case.assertions or [])
        ]
        result.assertion_results = assertion_results
        result.status = "pass" if all(r["passed"] for r in assertion_results) else "fail"
    except Exception as exc:  # noqa: BLE001 - execution errors are recorded, not raised
        result.status = "error"
        result.error = str(exc)

    result.finished_at = datetime.now(timezone.utc)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
