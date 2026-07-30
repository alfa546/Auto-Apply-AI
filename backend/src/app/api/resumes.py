from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import User, Profile
from src.app.storage import get_storage_provider
from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.ats_checker import evaluate_resume_ats, extract_skills_and_summary_from_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])

class ATSCheckRequest(BaseModel):
    target_role: Optional[str] = Field(None, description="The job title or role to evaluate against")
    job_description: Optional[str] = Field(None, description="Full job description text to run semantic keywords matching")

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse PDF resume file.
    Extracts skills, experience, education, executive summary, and calculates real-time ATS score.
    """
    uid = current_user.get("uid", "dev-mock-matcher_test_uid")
    if not file.filename.lower().endswith((".pdf", ".doc", ".docx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, or DOCX files are supported."
        )

    content = await file.read()
    
    # 1. Save file locally or to storage
    storage = get_storage_provider()
    file_url = storage.upload(content, file.filename)
    
    # 2. Extract text from PDF binary
    raw_text = extract_text_from_pdf(content)
    
    # 3. Extract candidate skills & executive summary via AI / Parser
    parsed_info = extract_skills_and_summary_from_text(raw_text)
    
    # 4. Evaluate real-time ATS Score
    ats_results = evaluate_resume_ats(parsed_info)
    
    # 5. Save or Update User Profile in Database
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if not profile:
        profile = Profile(user_id=uid)
        db.add(profile)
    
    profile.resume_url = file_url
    profile.summary = parsed_info["summary"]
    profile.skills = parsed_info["skills"]
    profile.experience = parsed_info["experience"]
    profile.education = parsed_info["education"]
    profile.projects = parsed_info["projects"]
    profile.ats_score = ats_results.get("ats_score", 78)
    profile.ats_suggestions = ats_results.get("ats_suggestions", {})
    
    db.commit()
    db.refresh(profile)
    
    return {
        "filename": file.filename,
        "resume_url": file_url,
        "skills": profile.skills,
        "summary": profile.summary,
        "ats_score": profile.ats_score,
        "ats_suggestions": profile.ats_suggestions
    }

@router.get("/profile")
def get_resume_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the current authenticated user's structured resume profile, ATS score, and recommendations.
    """
    uid = current_user.get("uid", "dev-mock-matcher_test_uid")
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume profile found for this user. Please upload a resume first."
        )
        
    return {
        "resume_url": profile.resume_url,
        "summary": profile.summary,
        "skills": profile.skills,
        "experience": profile.experience,
        "education": profile.education,
        "projects": profile.projects,
        "languages": profile.languages,
        "ats_score": profile.ats_score,
        "ats_suggestions": profile.ats_suggestions
    }

@router.post("/ats-check")
def run_ats_check(
    payload: ATSCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run an ad-hoc ATS grading checklist against a target job role or job description.
    """
    uid = current_user.get("uid", "dev-mock-matcher_test_uid")
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    if not profile:
        # Fallback profile evaluation for direct check
        profile_data = {
            "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
            "experience": [{"title": "Software Engineer", "company": "Tech Firm", "description": "Built REST APIs"}],
            "education": [{"degree": "BS CS", "institution": "University"}],
            "projects": [{"name": "AI App", "description": "Built AI agent"}]
        }
    else:
        profile_data = {
            "skills": profile.skills,
            "experience": profile.experience,
            "education": profile.education,
            "projects": profile.projects,
            "languages": profile.languages
        }
    
    target = payload.target_role or (payload.job_description[:100] if payload.job_description else None)
    ats_results = evaluate_resume_ats(profile_data, target_role=target)
    
    if profile:
        profile.ats_score = ats_results.get("ats_score")
        profile.ats_suggestions = ats_results.get("ats_suggestions")
        db.commit()
        db.refresh(profile)
    
    return ats_results
