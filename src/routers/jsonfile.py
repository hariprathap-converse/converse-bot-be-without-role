from fastapi import APIRouter, Depends, UploadFile, File,HTTPException
import json
import os
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from src.crud.jsonfile import save_file,get_all_files,get_file_by_id,delete_file
from src.core.database import get_db  # Assuming you have a get_db dependency

router = APIRouter()

@router.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    uploaded_files = []
    for file in files:
        content = await file.read()  # Read file content as bytes
        file_record = save_file(db, filename=file.filename, content=content)
        uploaded_files.append({"id": file_record.id, "filename": file_record.filename})
    return {"uploaded_files": uploaded_files}


@router.get("/files/")
def read_all_files(db: Session = Depends(get_db)):
    files = get_all_files(db)
    return {"files": [{"id": f.id, "filename": f.filename} for f in files]}

@router.get("/files/{file_id}")
def read_file(file_id: int, db: Session = Depends(get_db)):
    file = get_file_by_id(db, file_id)
    if not file:
        return {"error": "File not found"}
    content_str = file.content.decode('utf-8')
    try:
            content_json = json.loads(content_str)  # Convert string to JSON object
    except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="File content is not valid JSON")

        # Return the content as JSON
    return {"filename": file.filename, "content": content_json}
    # return {"id": file.id, "filename": file.filename, "content": file.content.decode('utf-8', errors='ignore')}

@router.delete("/files/{file_id}")
def delete_file_record(file_id: int, db: Session = Depends(get_db)):
    success = delete_file(db, file_id)
    if not success:
        return {"error": "File not found"}
    return {"message": "File deleted successfully"}



@router.get("/get/file/local")
def get_files_locally(db: Session = Depends(get_db)):
    # Fetch all files from the database
    files = get_all_files(db)

    # Directory to store the files locally
    output_dir = "json-output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it doesn't exist

    stored_files = []
    for file in files:
        file_path = os.path.join(output_dir, file.filename)

        # Write file content to the local file
        with open(file_path, "wb") as f:
            f.write(file.content)
        stored_files.append(file_path)

    return JSONResponse(
        content={"message": "Files stored locally", "stored_files": stored_files},
        status_code=200
    )
