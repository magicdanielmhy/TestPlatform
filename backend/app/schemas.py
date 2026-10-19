from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Assertion(BaseModel):
    type: Literal["status", "body"]
    expected: Any
    operator: Literal["equals", "contains"] = "contains"


class TestCaseBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    method: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    headers: dict[str, str] = {}
    body: str = ""
    assertions: list[Assertion] = []


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[dict[str, str]] = None
    body: Optional[str] = None
    assertions: Optional[list[Assertion]] = None


class TestCaseOut(TestCaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestCaseSetCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""


class TestCaseSetOut(BaseModel):
    id: int
    name: str
    description: str
    member_count: int
    created_at: datetime
    updated_at: datetime


class TestCaseSetDetail(BaseModel):
    id: int
    name: str
    description: str
    members: list[TestCaseOut]
    created_at: datetime
    updated_at: datetime


class AddMemberRequest(BaseModel):
    test_case_id: int


class ExecutionResultOut(BaseModel):
    id: int
    test_case_id: int
    set_run_id: Optional[int] = None
    status: str
    request_snapshot: dict
    response_status: Optional[int] = None
    response_body: str = ""
    assertion_results: list = []
    error: str = ""
    started_at: datetime
    finished_at: datetime

    model_config = {"from_attributes": True}


class SetRunOut(BaseModel):
    set_run_id: int
    total: int
    passed: int
    failed: int
    errors: int
    results: list[ExecutionResultOut]
