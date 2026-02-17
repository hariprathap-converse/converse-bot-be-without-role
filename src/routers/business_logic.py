from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.core.authentication import get_current_employee, roles_required
from src.core.database import get_db
from src.core.utils import send_email_leave
from src.crud.business_logic import create_employee_leave_logic
from src.schemas.leave import EmployeeLeaveCreate

router = APIRouter(
    prefix="/leave", tags=["leave"], responses={400: {"detail": "Not found"}}
)


@router.post(
    "/", dependencies=[Depends(roles_required("employee", "admin", "teamlead"))]
)
async def apply_leave_logic(
    leave: EmployeeLeaveCreate,
    db: Session = Depends(get_db),
    current_employee=Depends(get_current_employee),
    # Ensure this is the correct type
):
    # Accessing employee_id directly from the object
    employee_id = current_employee.employment_id
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Employee data Please Authenticate ",
        )
    db_leave = create_employee_leave_logic(db, leave, employee_id)
    email_leav = db_leave["employee_email"]
    await send_email_leave(
        db_leave["employee_email"],
        db_leave["employee_firstname"],
        db_leave["employee_lastname"],
        db_leave["leave"],
        db_leave["reason"],
        db_leave["status"],
        db_leave["other_entries"],
    )
    return {
        "details": f"leave applied successfully for '{employee_id}' check your mail '{email_leav}'"
    }
