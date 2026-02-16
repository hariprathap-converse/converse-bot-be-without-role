from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.core.salary_database import get_salary_db
from src.models.salary_models import Employee, Department, Position, Incentive

router = APIRouter(tags=["salary-data"])

@router.get("/salary-data")
def get_salary_data(db: Session = Depends(get_salary_db)):
    # Fetch employees with relationships
    employees = db.query(Employee).all()
    
    # Calculate incentive totals
    employee_data = []
    for emp in employees:
        total_incentive = sum(inc.amount for inc in emp.incentives)
        
        dept_colors = {
            "bg": emp.department.color_bg,
            "text": emp.department.color_text,
            "border": emp.department.color_border
        }
        
        # Build department cell config dynamically if needed, 
        # or rely on the static config structure below with updated colorMap
        
        employee_data.append({
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
            "incentive": total_incentive
        })

    # Department colors for the config
    departments = db.query(Department).all()
    color_map = {}
    for dept in departments:
        color_map[dept.name] = {
            "bg": dept.color_bg,
            "text": dept.color_text,
            "border": dept.color_border
        }

    response = {
      "title": "Employee Performance Dashboard",
      "description": "Displays employee performance, compensation, and engagement metrics across departments for monitoring workforce productivity and growth.",
      "tableName": "employee_performance",
      "tableDescription": "Contains employee profile, role, salary, performance score, and project contribution details used for analytics dashboards.",
      "columns": [
        {
          "accessorKey": "employee",
          "header": "Employee",
          "description": "Employee name and profile identity used for display with avatar.",
          "width": 200,
          "cellType": "avatar",
        },
        {
          "accessorKey": "department",
          "header": "Department",
          "description": "Department to which the employee belongs.",
          "width": 140,
          "cellType": "badge",
          "cellConfig": {
            "colorMap": color_map
          },
        },
        {
          "accessorKey": "position",
          "header": "Position",
          "description": "Employee job title or role in the organization.",
          "width": 180,
          "cellType": "text",
        },
        {
          "accessorKey": "salary",
          "header": "Salary",
          "description": "Employee base salary used for compensation analytics.",
          "width": 130,
          "type": "number",
          "defaultChartType": "line",
          "cellType": "currency",
          "cellConfig": {
            "currency": "USD",
            "locale": "en-US",
          },
        },
        {
            "accessorKey": "incentive",
            "header": "Incentive",
            "description": "Total incentive amount for the employee.",
            "width": 130,
            "type": "number",
            "cellType": "currency",
            "cellConfig": {
                "currency": "USD",
                "locale": "en-US",
            },
        },
        {
          "accessorKey": "performance",
          "header": "Performance",
          "description": "Performance score representing employee evaluation metrics.",
          "width": 150,
          "type": "number",
          "defaultChartType": "bar",
          "cellType": "progress",
          "cellConfig": {
            "max": 100,
            "showPercentage": True,
          },
        },
        {
          "accessorKey": "status",
          "header": "Status",
          "description": "Current employment status such as Active, On Leave, or Resigned.",
          "width": 120,
          "cellType": "status",
        },
        {
          "accessorKey": "growth",
          "header": "Growth",
          "description": "Indicates employee growth trend based on recent performance cycles.",
          "width": 110,
          "cellType": "badge",
        },
        {
          "accessorKey": "joinDate",
          "header": "Join Date",
          "description": "Date when the employee joined the organization.",
          "width": 130,
          "cellType": "date",
          "cellConfig": {
            "format": "short",
          },
        },
        {
          "accessorKey": "projects",
          "header": "Projects",
          "description": "Number of projects the employee is currently assigned to.",
          "width": 100,
          "type": "number",
          "cellType": "number",
        },
      ],
      "data": employee_data,
      "options": {
        "enableSorting": True,
        "enableFiltering": True,
        "enablePagination": True,
        "enableRowSelection": True,
        "enableColumnPinning": True,
        "enableDensity": True,
        "defaultPageSize": 10,
        "searchColumn": "employee",
      },
    }
    
    return response
