import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SALARY_DB_URL = os.getenv("SALARY_DB_URL")

salary_engine = create_engine(SALARY_DB_URL, pool_pre_ping=True)
SalarySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=salary_engine)
SalaryBase = declarative_base()


def get_salary_db():
    db = SalarySessionLocal()
    try:
        yield db
    finally:
        db.close()
