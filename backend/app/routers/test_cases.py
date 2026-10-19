from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..execution import execute_case
from ..models import ExecutionResult, TestCase
from ..schemas import ExecutionResultOut, TestCaseCreate, TestCaseOut, TestCaseUpdate
from ..security import get_current_user

router = APIRouter(
    prefix="/api/test-cases",
    tags=["test-cases"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[TestCaseOut])
def list_cases(db: Session = Depends(get_db)):
    return db.query(TestCase).order_by(TestCase.updated_at.desc()).all()


@router.post("", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
def create_case(body: TestCaseCreate, db: Session = Depends(get_db)):
    test_case = TestCase(**body.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.get("/{case_id}", response_model=TestCaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.put("/{case_id}", response_model=TestCaseOut)
def update_case(case_id: int, body: TestCaseUpdate, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(test_case, key, value)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    db.delete(test_case)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{case_id}/execute", response_model=ExecutionResultOut)
def execute_single_case(case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return execute_case(test_case, db)


@router.get("/{case_id}/executions", response_model=list[ExecutionResultOut])
def list_case_executions(case_id: int, db: Session = Depends(get_db)):
    test_case = db.get(TestCase, case_id)
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return (
        db.query(ExecutionResult)
        .filter(ExecutionResult.test_case_id == case_id)
        .order_by(ExecutionResult.started_at.desc())
        .all()
    )
