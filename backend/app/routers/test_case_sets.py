from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..execution import execute_case, new_run_id
from ..models import SetMember, TestCase, TestCaseSet
from ..schemas import (
    AddMemberRequest,
    SetRunOut,
    TestCaseSetCreate,
    TestCaseSetDetail,
    TestCaseSetOut,
)
from ..security import get_current_user

router = APIRouter(
    prefix="/api/test-case-sets",
    tags=["test-case-sets"],
    dependencies=[Depends(get_current_user)],
)


def _set_out(db: Session, s: TestCaseSet) -> TestCaseSetOut:
    count = db.query(SetMember).filter(SetMember.set_id == s.id).count()
    return TestCaseSetOut(
        id=s.id,
        name=s.name,
        description=s.description,
        member_count=count,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _members(db: Session, set_id: int) -> list[TestCase]:
    return (
        db.query(TestCase)
        .join(SetMember, SetMember.test_case_id == TestCase.id)
        .filter(SetMember.set_id == set_id)
        .order_by(TestCase.id)
        .all()
    )


@router.get("", response_model=list[TestCaseSetOut])
def list_sets(db: Session = Depends(get_db)):
    sets = db.query(TestCaseSet).order_by(TestCaseSet.updated_at.desc()).all()
    return [_set_out(db, s) for s in sets]


@router.post("", response_model=TestCaseSetOut, status_code=status.HTTP_201_CREATED)
def create_set(body: TestCaseSetCreate, db: Session = Depends(get_db)):
    s = TestCaseSet(name=body.name, description=body.description)
    db.add(s)
    db.commit()
    db.refresh(s)
    return _set_out(db, s)


@router.get("/{set_id}", response_model=TestCaseSetDetail)
def get_set(set_id: int, db: Session = Depends(get_db)):
    s = db.get(TestCaseSet, set_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Test case set not found")
    return TestCaseSetDetail(
        id=s.id,
        name=s.name,
        description=s.description,
        members=_members(db, set_id),
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(set_id: int, db: Session = Depends(get_db)):
    s = db.get(TestCaseSet, set_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Test case set not found")
    db.query(SetMember).filter(SetMember.set_id == set_id).delete()
    db.delete(s)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{set_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(set_id: int, body: AddMemberRequest, db: Session = Depends(get_db)):
    s = db.get(TestCaseSet, set_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Test case set not found")
    test_case = db.get(TestCase, body.test_case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    existing = (
        db.query(SetMember)
        .filter(SetMember.set_id == set_id, SetMember.test_case_id == body.test_case_id)
        .first()
    )
    if existing is not None:
        return {"id": existing.id, "set_id": set_id, "test_case_id": body.test_case_id}
    member = SetMember(set_id=set_id, test_case_id=body.test_case_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return {"id": member.id, "set_id": set_id, "test_case_id": body.test_case_id}


@router.delete("/{set_id}/members/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(set_id: int, test_case_id: int, db: Session = Depends(get_db)):
    member = (
        db.query(SetMember)
        .filter(SetMember.set_id == set_id, SetMember.test_case_id == test_case_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(member)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{set_id}/execute", response_model=SetRunOut)
def execute_set(set_id: int, db: Session = Depends(get_db)):
    s = db.get(TestCaseSet, set_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Test case set not found")
    members = _members(db, set_id)
    run_id = new_run_id()
    results = [execute_case(tc, db, set_run_id=run_id) for tc in members]
    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    errors = sum(1 for r in results if r.status == "error")
    return SetRunOut(
        set_run_id=run_id,
        total=len(results),
        passed=passed,
        failed=failed,
        errors=errors,
        results=results,
    )
