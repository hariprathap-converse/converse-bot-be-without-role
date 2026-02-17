from sqlalchemy import JSON, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.core.salary_database import SalaryBase


class Department(SalaryBase):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    color_bg = Column(String(20))
    color_text = Column(String(20))
    color_border = Column(String(20))

    employees = relationship("Employee", back_populates="department")


class Position(SalaryBase):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, index=True)

    employees = relationship("Employee", back_populates="position")


class Employee(SalaryBase):
    __tablename__ = "employee_performance"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))
    salary = Column(Float)
    performance = Column(Integer)
    status = Column(String(50))
    growth = Column(String(20))
    join_date = Column(Date)
    projects = Column(Integer)

    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    incentives = relationship("Incentive", back_populates="employee")


class Incentive(SalaryBase):
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee_performance.id"))
    amount = Column(Float)
    date = Column(Date)

    employee = relationship("Employee", back_populates="incentives")


class TableMetadata(SalaryBase):
    __tablename__ = "table_metadata"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), unique=True, index=True)
    title = Column(String(200))
    description = Column(String(500))
    table_description = Column(String(500))
    options = Column(JSON, nullable=True)

    columns = relationship(
        "ColumnMetadata", back_populates="table", cascade="all, delete-orphan"
    )


class ColumnMetadata(SalaryBase):
    __tablename__ = "column_metadata"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_metadata.id"))
    accessor_key = Column(String(100))
    header = Column(String(100))
    description = Column(String(500))
    width = Column(Integer)
    type = Column(String(50))  # 'number', 'string', etc.
    cell_type = Column(String(50))  # 'avatar', 'badge', 'currency', etc.
    cell_config = Column(JSON, nullable=True)
    default_chart_type = Column(String(50), nullable=True)

    table = relationship("TableMetadata", back_populates="columns")
