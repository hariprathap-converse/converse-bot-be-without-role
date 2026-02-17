from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.salary_database import get_salary_db
from src.models.salary_models import (
    ColumnMetadata,
    Department,
    Employee,
    Incentive,
    Position,
    TableMetadata,
)

router = APIRouter(tags=["salary-data"])


@router.get("/salary-data")
def get_salary_data(
    table: str = "employee_performance", db: Session = Depends(get_salary_db)
):
    """
    Fetches table configuration and data dynamically based on the table name.
    """
    # 1. Fetch Table Metadata
    # Use scalar() or first() correctly
    table_meta = db.query(TableMetadata).filter_by(table_name=table).first()
    if not table_meta:
        # Fallback for dev/test if seed didn't run or table name mismatch,
        # but in prod we should raise 404.
        # Let's return 404 to be strict.
        raise HTTPException(
            status_code=404, detail=f"Table metadata not found for '{table}'"
        )

    # 2. Fetch Column Metadata
    # Sorted by id (insertion order)
    columns_meta = (
        db.query(ColumnMetadata)
        .filter_by(table_id=table_meta.id)
        .order_by(ColumnMetadata.id)
        .all()
    )

    # 3. Department colors (needed for dynamic color map resolution)
    departments = db.query(Department).all()
    color_map = {}
    for dept in departments:
        color_map[dept.name] = {
            "bg": dept.color_bg,
            "text": dept.color_text,
            "border": dept.color_border,
        }

    # 4. Construct Columns Configuration
    columns_config = []
    for col in columns_meta:
        col_def = {
            "accessorKey": col.accessor_key,
            "header": col.header,
            "description": col.description,
            "width": col.width,
            "cellType": col.cell_type,
        }

        if col.type:
            col_def["type"] = col.type

        if col.default_chart_type:
            col_def["defaultChartType"] = col.default_chart_type

        if col.cell_config:
            # Deep copy or modify to inject dynamic values
            config = col.cell_config.copy() if isinstance(col.cell_config, dict) else {}
            if config.get("colorMap") == "dynamic":
                config["colorMap"] = color_map
            col_def["cellConfig"] = config

        columns_config.append(col_def)

    # 5. Fetch Data (Strategy Pattern for multiple tables)
    data_rows = []

    if table == "employee_performance":
        employees = db.query(Employee).all()
        for emp in employees:
            total_incentive = sum(inc.amount for inc in emp.incentives)

            data_rows.append(
                {
                    "id": str(emp.id),
                    "employee": emp.name,
                    "department": emp.department.name,
                    "position": emp.position.title,
                    "salary": emp.salary,
                    "performance": emp.performance,
                    "status": emp.status,
                    "growth": emp.growth,
                    "joinDate": emp.join_date.isoformat(),
                    "projects": emp.projects,
                    "incentive": total_incentive,
                }
            )
    else:
        # Placeholder for other tables
        data_rows = []

    # 6. Construct Final Response
    response = {
        "title": table_meta.title,
        "description": table_meta.description,
        "tableName": table_meta.table_name,
        "tableDescription": table_meta.table_description,
        "columns": columns_config,
        "data": data_rows,
        "options": table_meta.options or {},
    }

    return response
