from sqlalchemy.orm import Session

from src.models.jsonfile import FileModel


def save_file(db: Session, filename: str, content: bytes):
    file_record = FileModel(filename=filename, content=content)
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record


def get_all_files(db: Session):
    return db.query(FileModel).all()


# Get a file by ID
def get_file_by_id(db: Session, file_id: int):
    return db.query(FileModel).filter(FileModel.id == file_id).first()


# Delete a file
def delete_file(db: Session, file_id: int):
    file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file_record:
        return False  # Return False if the file does not exist
    db.delete(file_record)
    db.commit()
    return True
