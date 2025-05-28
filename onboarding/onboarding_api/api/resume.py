from fastapi import APIRouter, UploadFile, File, Form
from services.resume_service import extract_resume_experience
from db.resume_repository import store_uploaded_resume

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    user_id: str = Form(...),
    region: str = Form(...),
    file: UploadFile = File(...)
):
    # Save file and store to DB
    resume_path = store_uploaded_resume(file, user_id, region)
    
    # Extract structured experience
    experiences = extract_resume_experience(file, user_id, region)
    
    return {
        "status": "success",
        "resume_path": resume_path,
        "extracted_experience": experiences
    }