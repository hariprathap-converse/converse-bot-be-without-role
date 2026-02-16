import sys
import os
import random
from datetime import datetime, timedelta

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.salary_database import salary_engine, SalaryBase, SalarySessionLocal
from src.models.salary_models import Department, Position, Employee, Incentive, TableMetadata, ColumnMetadata

# Data from sample-data.ts
raw_data = [
    {
      "id": "1",
      "employee": "Sarah Johnson",
      "department": "Engineering",
      "position": "Senior Software Engineer",
      "salary": 125000,
      "performance": 92,
      "status": "Active",
      "growth": "+15.2%",
      "joinDate": "2021-03-15",
      "projects": 12,
    },
    {
      "id": "2",
      "employee": "Michael Chen",
      "department": "Sales",
      "position": "Sales Director",
      "salary": 145000,
      "performance": 88,
      "status": "Active",
      "growth": "+22.5%",
      "joinDate": "2020-01-20",
      "projects": 8,
    },
    {
      "id": "3",
      "employee": "Emily Rodriguez",
      "department": "Marketing",
      "position": "Marketing Manager",
      "salary": 98000,
      "performance": 85,
      "status": "Active",
      "growth": "+18.3%",
      "joinDate": "2021-07-10",
      "projects": 15,
    },
    {
      "id": "4",
      "employee": "David Kim",
      "department": "Engineering",
      "position": "DevOps Engineer",
      "salary": 115000,
      "performance": 90,
      "status": "Active",
      "growth": "+12.8%",
      "joinDate": "2022-02-01",
      "projects": 10,
    },
    {
      "id": "5",
      "employee": "Jessica Williams",
      "department": "HR",
      "position": "HR Manager",
      "salary": 92000,
      "performance": 78,
      "status": "Active",
      "growth": "+8.5%",
      "joinDate": "2020-11-05",
      "projects": 6,
    },
    {
      "id": "6",
      "employee": "Robert Taylor",
      "department": "Finance",
      "position": "Financial Analyst",
      "salary": 88000,
      "performance": 82,
      "status": "Active",
      "growth": "+10.2%",
      "joinDate": "2021-09-12",
      "projects": 7,
    },
    {
      "id": "7",
      "employee": "Amanda Martinez",
      "department": "Engineering",
      "position": "Frontend Developer",
      "salary": 105000,
      "performance": 87,
      "status": "Active",
      "growth": "+14.7%",
      "joinDate": "2022-04-18",
      "projects": 9,
    },
    {
      "id": "8",
      "employee": "James Anderson",
      "department": "Sales",
      "position": "Account Executive",
      "salary": 78000,
      "performance": 75,
      "status": "Pending",
      "growth": "+5.3%",
      "joinDate": "2023-01-08",
      "projects": 4,
    },
    {
      "id": "9",
      "employee": "Lisa Thompson",
      "department": "Operations",
      "position": "Operations Manager",
      "salary": 102000,
      "performance": 84,
      "status": "Active",
      "growth": "+11.9%",
      "joinDate": "2021-05-22",
      "projects": 11,
    },
    {
      "id": "10",
      "employee": "Christopher Lee",
      "department": "Engineering",
      "position": "Backend Developer",
      "salary": 110000,
      "performance": 89,
      "status": "Active",
      "growth": "+16.4%",
      "joinDate": "2021-12-03",
      "projects": 13,
    },
    {
      "id": "11",
      "employee": "Michelle Garcia",
      "department": "Marketing",
      "position": "Content Strategist",
      "salary": 72000,
      "performance": 80,
      "status": "Active",
      "growth": "+9.1%",
      "joinDate": "2022-08-14",
      "projects": 8,
    },
    {
      "id": "12",
      "employee": "Daniel White",
      "department": "Finance",
      "position": "Senior Accountant",
      "salary": 95000,
      "performance": 86,
      "status": "Active",
      "growth": "+13.2%",
      "joinDate": "2020-06-30",
      "projects": 5,
    },
    {
      "id": "13",
      "employee": "Jennifer Harris",
      "department": "HR",
      "position": "Recruiter",
      "salary": 68000,
      "performance": 77,
      "status": "Active",
      "growth": "+7.8%",
      "joinDate": "2022-10-25",
      "projects": 3,
    },
    {
      "id": "14",
      "employee": "Matthew Clark",
      "department": "Engineering",
      "position": "Tech Lead",
      "salary": 135000,
      "performance": 94,
      "status": "Active",
      "growth": "+19.6%",
      "joinDate": "2019-08-17",
      "projects": 16,
    },
    {
      "id": "15",
      "employee": "Ashley Lewis",
      "department": "Sales",
      "position": "Sales Manager",
      "salary": 112000,
      "performance": 83,
      "status": "Active",
      "growth": "+12.1%",
      "joinDate": "2021-02-09",
      "projects": 10,
    },
    {
      "id": "16",
      "employee": "Kevin Robinson",
      "department": "Operations",
      "position": "Supply Chain Analyst",
      "salary": 76000,
      "performance": 79,
      "status": "Active",
      "growth": "+6.9%",
      "joinDate": "2022-11-20",
      "projects": 6,
    },
    {
      "id": "17",
      "employee": "Rachel Walker",
      "department": "Marketing",
      "position": "Brand Manager",
      "salary": 89000,
      "performance": 81,
      "status": "Active",
      "growth": "+10.5%",
      "joinDate": "2021-04-12",
      "projects": 9,
    },
    {
      "id": "18",
      "employee": "Brandon Hall",
      "department": "Engineering",
      "position": "Mobile Developer",
      "salary": 108000,
      "performance": 88,
      "status": "Active",
      "growth": "+15.8%",
      "joinDate": "2022-01-28",
      "projects": 11,
    },
    {
      "id": "19",
      "employee": "Stephanie Allen",
      "department": "Finance",
      "position": "Budget Analyst",
      "salary": 82000,
      "performance": 76,
      "status": "Pending",
      "growth": "+4.2%",
      "joinDate": "2023-03-05",
      "projects": 4,
    },
    {
      "id": "20",
      "employee": "Justin Young",
      "department": "Sales",
      "position": "Business Development",
      "salary": 85000,
      "performance": 84,
      "status": "Active",
      "growth": "+11.3%",
      "joinDate": "2021-10-16",
      "projects": 7,
    },
    {
      "id": "21",
      "employee": "Nicole King",
      "department": "HR",
      "position": "Training Specialist",
      "salary": 71000,
      "performance": 78,
      "status": "Active",
      "growth": "+8.7%",
      "joinDate": "2022-05-30",
      "projects": 5,
    },
    {
      "id": "22",
      "employee": "Ryan Wright",
      "department": "Engineering",
      "position": "QA Engineer",
      "salary": 92000,
      "performance": 85,
      "status": "Active",
      "growth": "+12.4%",
      "joinDate": "2021-11-08",
      "projects": 10,
    },
    {
      "id": "23",
      "employee": "Megan Lopez",
      "department": "Marketing",
      "position": "Social Media Manager",
      "salary": 67000,
      "performance": 82,
      "status": "Active",
      "growth": "+9.8%",
      "joinDate": "2022-07-19",
      "projects": 12,
    },
    {
      "id": "24",
      "employee": "Tyler Hill",
      "department": "Operations",
      "position": "Logistics Coordinator",
      "salary": 69000,
      "performance": 74,
      "status": "Active",
      "growth": "+5.6%",
      "joinDate": "2023-02-14",
      "projects": 5,
    },
    {
      "id": "25",
      "employee": "Brittany Scott",
      "department": "Finance",
      "position": "Tax Specialist",
      "salary": 91000,
      "performance": 87,
      "status": "Active",
      "growth": "+14.1%",
      "joinDate": "2020-09-23",
      "projects": 6,
    },
    {
      "id": "26",
      "employee": "Eric Green",
      "department": "Engineering",
      "position": "Data Engineer",
      "salary": 118000,
      "performance": 91,
      "status": "Active",
      "growth": "+17.3%",
      "joinDate": "2021-06-07",
      "projects": 14,
    },
    {
      "id": "27",
      "employee": "Samantha Adams",
      "department": "Sales",
      "position": "Regional Sales Rep",
      "salary": 74000,
      "performance": 80,
      "status": "Active",
      "growth": "+8.9%",
      "joinDate": "2022-09-11",
      "projects": 6,
    },
    {
      "id": "28",
      "employee": "Gregory Baker",
      "department": "Marketing",
      "position": "SEO Specialist",
      "salary": 70000,
      "performance": 79,
      "status": "Active",
      "growth": "+7.5%",
      "joinDate": "2022-12-01",
      "projects": 8,
    },
    {
      "id": "29",
      "employee": "Kimberly Nelson",
      "department": "HR",
      "position": "Benefits Administrator",
      "salary": 66000,
      "performance": 75,
      "status": "Active",
      "growth": "+6.2%",
      "joinDate": "2023-01-22",
      "projects": 3,
    },
    {
      "id": "30",
      "employee": "Jonathan Carter",
      "department": "Engineering",
      "position": "Security Engineer",
      "salary": 128000,
      "performance": 93,
      "status": "Active",
      "growth": "+18.9%",
      "joinDate": "2020-04-15",
      "projects": 15,
    },
    {
      "id": "31",
      "employee": "Angela Mitchell",
      "department": "Operations",
      "position": "Process Improvement Lead",
      "salary": 97000,
      "performance": 86,
      "status": "Active",
      "growth": "+13.7%",
      "joinDate": "2021-08-28",
      "projects": 9,
    },
    {
      "id": "32",
      "employee": "Nicholas Perez",
      "department": "Finance",
      "position": "Investment Analyst",
      "salary": 99000,
      "performance": 84,
      "status": "Active",
      "growth": "+11.6%",
      "joinDate": "2021-03-19",
      "projects": 7,
    },
    {
      "id": "33",
      "employee": "Melissa Roberts",
      "department": "Sales",
      "position": "Customer Success Manager",
      "salary": 87000,
      "performance": 88,
      "status": "Active",
      "growth": "+15.4%",
      "joinDate": "2021-12-10",
      "projects": 11,
    },
    {
      "id": "34",
      "employee": "Andrew Turner",
      "department": "Engineering",
      "position": "Cloud Architect",
      "salary": 142000,
      "performance": 95,
      "status": "Active",
      "growth": "+21.2%",
      "joinDate": "2019-11-03",
      "projects": 18,
    },
    {
      "id": "35",
      "employee": "Laura Phillips",
      "department": "Marketing",
      "position": "Product Marketing Manager",
      "salary": 94000,
      "performance": 85,
      "status": "Active",
      "growth": "+12.9%",
      "joinDate": "2021-05-14",
      "projects": 10,
    },
    {
      "id": "36",
      "employee": "Brian Campbell",
      "department": "Operations",
      "position": "Warehouse Manager",
      "salary": 79000,
      "performance": 77,
      "status": "Active",
      "growth": "+7.1%",
      "joinDate": "2022-06-23",
      "projects": 5,
    },
    {
      "id": "37",
      "employee": "Christina Parker",
      "department": "HR",
      "position": "Employee Relations Specialist",
      "salary": 73000,
      "performance": 81,
      "status": "Active",
      "growth": "+9.4%",
      "joinDate": "2022-03-17",
      "projects": 6,
    },
    {
      "id": "38",
      "employee": "Steven Evans",
      "department": "Engineering",
      "position": "Full Stack Developer",
      "salary": 112000,
      "performance": 89,
      "status": "Active",
      "growth": "+16.1%",
      "joinDate": "2021-09-29",
      "projects": 12,
    },
    {
      "id": "39",
      "employee": "Rebecca Edwards",
      "department": "Finance",
      "position": "Controller",
      "salary": 132000,
      "performance": 92,
      "status": "Active",
      "growth": "+17.8%",
      "joinDate": "2019-12-08",
      "projects": 8,
    },
    {
      "id": "40",
      "employee": "Patrick Collins",
      "department": "Sales",
      "position": "VP of Sales",
      "salary": 165000,
      "performance": 96,
      "status": "Active",
      "growth": "+24.3%",
      "joinDate": "2018-07-21",
      "projects": 14,
    },
    {
      "id": "41",
      "employee": "Karen Stewart",
      "department": "Marketing",
      "position": "Creative Director",
      "salary": 108000,
      "performance": 90,
      "status": "Active",
      "growth": "+16.7%",
      "joinDate": "2020-10-12",
      "projects": 13,
    },
    {
      "id": "42",
      "employee": "Timothy Sanchez",
      "department": "Engineering",
      "position": "AI/ML Engineer",
      "salary": 138000,
      "performance": 94,
      "status": "Active",
      "growth": "+20.5%",
      "joinDate": "2020-05-26",
      "projects": 16,
    },
]

# Department colors configuration
department_colors = {
    "Engineering": { "bg": "#dbeafe", "text": "#1e40af", "border": "#93c5fd" },
    "Sales": { "bg": "#dcfce7", "text": "#166534", "border": "#86efac" },
    "Marketing": { "bg": "#fce7f3", "text": "#9f1239", "border": "#fbcfe8" },
    "HR": { "bg": "#fef3c7", "text": "#92400e", "border": "#fde68a" },
    "Finance": { "bg": "#e0e7ff", "text": "#3730a3", "border": "#c7d2fe" },
    "Operations": { "bg": "#f3e8ff", "text": "#6b21a8", "border": "#e9d5ff" },
}

def seed_data():
    # Create tables
    SalaryBase.metadata.create_all(salary_engine)
    
    db = SalarySessionLocal()
    
    try:
        # Check if data already exists to avoid duplication
        if db.query(Employee).count() > 0:
            print("Employe data already exists.")
        else:
            print("Seeding employee data...")

            # 1. Departments and Positions
            departments = {}
            positions = {}

            for row in raw_data:
                dept_name = row["department"]
                pos_title = row["position"]
                
                # Create Department if not exists
                if dept_name not in departments:
                    colors = department_colors.get(dept_name, { "bg": "#ffffff", "text": "#000000", "border": "#cccccc" })
                    dept = Department(
                        name=dept_name,
                        color_bg=colors["bg"],
                        color_text=colors["text"],
                        color_border=colors["border"]
                    )
                    db.add(dept)
                    db.flush() # flush to get ID
                    departments[dept_name] = dept
                
                # Create Position if not exists
                if pos_title not in positions:
                    pos = Position(title=pos_title)
                    db.add(pos)
                    db.flush()
                    positions[pos_title] = pos

            # 2. Employees and Incentives
            for row in raw_data:
                emp = Employee(
                    name=row["employee"],
                    department_id=departments[row["department"]].id,
                    position_id=positions[row["position"]].id,
                    salary=row["salary"],
                    performance=row["performance"],
                    status=row["status"],
                    growth=row["growth"],
                    join_date=datetime.strptime(row["joinDate"], "%Y-%m-%d").date(),
                    projects=row["projects"]
                )
                db.add(emp)
                db.flush()
                
                # Generate 1-3 random incentives for each employee
                num_incentives = random.randint(1, 3)
                for _ in range(num_incentives):
                    # Random incentive amount between 1% and 10% of salary/12
                    amount = round(emp.salary / 12 * random.uniform(0.01, 0.10), 2)
                    # Random date within last year
                    date_offset = random.randint(0, 365)
                    date = datetime.now().date() - timedelta(days=date_offset)
                    
                    incentive = Incentive(
                        employee_id=emp.id,
                        amount=amount,
                        date=date
                    )
                    db.add(incentive)

            db.commit()
            print("Employee seeding completed successfully!")

        # 3. Seed Table Metadata
        if db.query(TableMetadata).filter_by(table_name="employee_performance").first():
            print("Metadata already exists. Skipping metadata seed.")
        else:
            print("Seeding metadata...")
            table_meta = TableMetadata(
                table_name="employee_performance",
                title="Employee Performance Dashboard",
                description="Displays employee performance, compensation, and engagement metrics across departments for monitoring workforce productivity and growth.",
                table_description="Contains employee profile, role, salary, performance score, and project contribution details used for analytics dashboards.",
                options={
                    "enableSorting": True,
                    "enableFiltering": True,
                    "enablePagination": True,
                    "enableRowSelection": True,
                    "enableColumnPinning": True,
                    "enableDensity": True,
                    "defaultPageSize": 10,
                    "searchColumn": "employee",
                }
            )
            db.add(table_meta)
            db.flush()

            # Seed Column Metadata
            columns_data = [
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
                    "cellConfig": { "colorMap": "dynamic" }, # Dynamic map will be resolved in API
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
            ]

            for col in columns_data:
                column_meta = ColumnMetadata(
                    table_id=table_meta.id,
                    accessor_key=col["accessorKey"],
                    header=col["header"],
                    description=col.get("description"),
                    width=col.get("width"),
                    type=col.get("type"),
                    cell_type=col.get("cellType"),
                    cell_config=col.get("cellConfig"),
                    default_chart_type=col.get("defaultChartType")
                )
                db.add(column_meta)
            
            db.commit()
            print("Metadata seeding completed!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
