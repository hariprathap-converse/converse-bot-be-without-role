from sqlalchemy import Column, Integer, LargeBinary, String, create_engine

from src.core.database import Base


class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    content = Column(LargeBinary)
