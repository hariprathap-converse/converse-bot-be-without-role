from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.employee import EmployeeEmploymentDetails
from src.models.leave import EmployeeLeave, LeaveCalendar, LeaveDuration
from src.models.personal import EmployeeOnboarding
from src.models.role import Role
from src.schemas.leave import EmployeeLeaveCreate


def create_leave_balance(
    db: Session, employee_id: int, leave_type: str, leave_entries: list
):
    # Define mappings for leave types
    leave_fields = {
        "sick": (
            "sick_leave",
            "Sick leave quota is exhausted. You cannot approve the additional sick leave.",
        ),
        "personal": (
            "personal_leave",
            "Personal leave quota is exhausted. You cannot approve the additional personal leave.",
        ),
        "vacation": (
            "vacation_leave",
            "Vacation leave quota is exhausted. You cannot approve the additional vacation leave.",
        ),
        "vacation": (
            "vacation_leave",
            "Vacation leave quota is exhausted. You cannot approve the additional vacation leave.",
        ),
        "unpaid": ("unpaid_leave", None),  # No quota check for unpaid leave
        "maternity": ("maternity_leave", None),  # No quota check for unpaid leave
    }

    # Retrieve the leave calendar entry for the given employee_id
    leave_calendar = (
        db.query(LeaveCalendar).filter(LeaveCalendar.employee_id == employee_id).first()
    )

    if not leave_calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LeaveCalendar entry not found for the specified employee {employee_id}.",
        )

    if leave_type not in leave_fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid leave type specified. Please use 'sick', 'personal', 'vacation', or 'unpaid' or 'maternity' for female .",
        )

    # Get the field name and error message from the mappings
    field_name, error_message = leave_fields[leave_type]

    # Handle unlimited unpaid leave case
    current_balance = getattr(leave_calendar, field_name)

    if leave_type == "unpaid":
        # No decrement or balance check, just return the calendar
        return leave_calendar

    if current_balance is not None and current_balance > 0:
        setattr(leave_calendar, field_name, current_balance - 1)

    else:
        leave_ids = [entry.id for entry in leave_entries if entry is not None]
        data = []
        for d in leave_ids:
            if d is not None:
                data.append(d)
        print(data)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This is the leave ID(s): {data} Please Note This id. This is No More  available {leave_type} leave. You cannot 'apply' {leave_type} Leave. Please select another option from '[sick', 'personal', 'vacation']. ",
        )

    # Commit the changes and handle exceptions
    try:
        db.commit()  # Commit the changes to the database
        # Refresh the instance to reflect updated data
        db.refresh(leave_calendar)
    except Exception as e:
        db.rollback()  # Roll back the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the leave balance.",
        )

    return leave_calendar


def create_employee_leave_logic(
    db: Session, leave: EmployeeLeaveCreate, employee_id: str
):
    leave_entries = []
    employee_data = (
        db.query(EmployeeEmploymentDetails)
        .filter(EmployeeEmploymentDetails.employee_id == employee_id)
        .first()
    )

    if not employee_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found",
        )

    # Check if there is an existing leave entry on the same date for this employee
    existing_leave = (
        db.query(EmployeeLeave)
        .filter(EmployeeLeave.employee_id == employee_data.id)
        .filter(EmployeeLeave.start_date == leave.start_date)
        .first()
    )
    find_gender = (
        db.query(EmployeeOnboarding)
        .filter(EmployeeOnboarding.employment_id == employee_data.employee_id)
        .first()
    )

    if employee_data.releave_date and employee_data.releave_date >= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave cannot be applied for employee when they in the time of notice period.",
        )

    if leave.leave_type.lower() == "maternity" and find_gender.gender != "female":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maternity leave is applicable only for female employees.",
        )
    if leave.total_days > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot apply for more than 3 consecutive days of leave.",
        )
    if existing_leave:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave entry already exists for the specified date .",
        )

    def map_leave_duration(leave_duration_str: str):
        if leave_duration_str.lower() == "oneday":
            return LeaveDuration.ONE_DAY
        elif leave_duration_str.lower() == "halfday":
            return LeaveDuration.HALF_DAY
        else:
            raise ValueError("Invalid leave duration")

    leave.duration = map_leave_duration(leave.duration.value)
    leave_type = leave.leave_type
    print(leave.start_date)
    print(leave.start_date.weekday())
    for i in range(leave.total_days):
        end_date = leave.start_date + timedelta(days=i)
        if end_date.weekday() >= 5:  # Saturday is 5, Sunday is 6
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave application cannot include weekends.",
            )
        db_leave = EmployeeLeave(
            employee_id=employee_data.id,
            leave_type=leave.leave_type,
            duration=leave.duration,
            start_date=leave.start_date + timedelta(days=i),
            end_date=end_date,
            reason=leave.reason,
        )

        leave_entries.append(db_leave)
        db.add(db_leave)

        # Call create_leave_balance and handle its return
        balance = create_leave_balance(db, employee_data.id, leave_type, leave_entries)
        print("Updated leave calendar:", balance)

    db.commit()
    employee_code = employee_data.employee_id
    employee_email = employee_data.employee_email
    employee_firstname = employee_data.employee.firstname
    employee_lastname = employee_data.employee.lastname
    other_leave_ids = [leave.id for leave in leave_entries]

    return {
        "leave": db_leave.id,
        "reason": db_leave.reason,
        "status": db_leave.status.value,
        "employee_email": employee_email,
        "employee_code": employee_code,
        "employee_firstname": employee_firstname,
        "employee_lastname": employee_lastname,
        "other_entries": other_leave_ids,
    }
