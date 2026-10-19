from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ExecutionResult
from ..schemas import ExecutionResultOut
from ..security import get_current_user

router = APIRouter(
    prefix="/api/executions",
    tags=["executions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ExecutionResultOut])
def list_executions(db: Session = Depends(get_db)):
    return (
        db.query(ExecutionResult)
        .order_by(ExecutionResult.started_at.desc())
        .limit(100)
        .all()
    )


@router.get("/{result_id}", response_model=ExecutionResultOut)
def get_execution(result_id: int, db: Session = Depends(get_db)):
    result = db.get(ExecutionResult, result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Execution result not found")
    return result
