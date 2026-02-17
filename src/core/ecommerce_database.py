import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

ECOM_DB_URL = os.getenv("ECOM_DB_URL")

ecom_engine = create_engine(ECOM_DB_URL, pool_pre_ping=True)

EcomSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ecom_engine)

EcomBase = declarative_base()


def get_ecom_db():
    db = EcomSessionLocal()
    try:
        yield db
    finally:
        db.close()
