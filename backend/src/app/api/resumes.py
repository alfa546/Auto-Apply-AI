from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import User, Profile, UserSettings
from src.app.storage import get_storage_provider
from src.app.config import settings
from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.ats_checker import evaluate_resume_ats, extract_skills_and_summary_from_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_UPLOAD_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_RESUME_EXTENSIONS = (".pdf", ".doc", ".docx", ".txt")


def validate_resume_upload(file: UploadFile, content: bytes):
    """Shared validation for resume uploads: extension, type and size."""
    filename = (file.filename or "").lower()
    if not filename.endswith(ALLOWED_RESUME_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, DOCX, or TXT files are supported.",
        )
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

class ATSCheckRequest(BaseModel):
    target_role: Optional[str] = Field(None, description="The job title or role to evaluate against")
    job_description: Optional[str] = Field(None, description="Full job description text to run semantic keywords matching")

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and parse PDF resume file.
    Extracts skills, experience, education, executive summary, and calculates real-time ATS score.
    """
    uid = current_user.id
    content = await file.read()

    # Validate extension, non-empty, and file size
    validate_resume_upload(file, content)

    # 1. Save file locally or to storage
    storage = get_storage_provider()
    file_url = storage.upload(content, file.filename)
    
    # 2. Extract text from PDF binary
    raw_text = extract_text_from_pdf(content)
    
    # Apply user's saved LLM API key for parsing (if available)
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if user_settings and user_settings.openai_api_key:
        import src.app.config as config_module
        if user_settings.llm_provider == "gemini" or user_settings.openai_api_key.startswith("AIzaSy"):
            config_module.settings.GEMINI_API_KEY = user_settings.openai_api_key
        else:
            config_module.settings.OPENAI_API_KEY = user_settings.openai_api_key
        if user_settings.llm_model:
            config_module.settings.OPENAI_MODEL = user_settings.llm_model

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
        "formatting_score": ats_results.get("formatting_score", 0),
        "keyword_density_score": ats_results.get("keyword_density_score", 0),
        "action_verbs_score": ats_results.get("action_verbs_score", 0),
        "section_completeness_score": ats_results.get("section_completeness_score", 0),
        "ats_suggestions": profile.ats_suggestions
    }

@router.get("/profile")
def get_resume_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the current authenticated user's structured resume profile, ATS score, and recommendations.
    """
    uid = current_user.id
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
        "formatting_score": getattr(profile, 'formatting_score', None),
        "keyword_density_score": getattr(profile, 'keyword_density_score', None),
        "action_verbs_score": getattr(profile, 'action_verbs_score', None),
        "section_completeness_score": getattr(profile, 'section_completeness_score', None),
        "ats_suggestions": profile.ats_suggestions
    }

@router.post("/ats-check")
def run_ats_check(
    payload: ATSCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run an ad-hoc ATS grading checklist against a target job role or job description.
    """
    uid = current_user.id
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume profile found for this user. Please upload a resume first to run an ATS check."
        )

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
    
    # Return all ATS data including 4 detailed scores
    return {
        "ats_score": ats_results.get("ats_score"),
        "formatting_score": ats_results.get("formatting_score", 0),
        "keyword_density_score": ats_results.get("keyword_density_score", 0),
        "action_verbs_score": ats_results.get("action_verbs_score", 0),
        "section_completeness_score": ats_results.get("section_completeness_score", 0),
        "ats_suggestions": ats_results.get("ats_suggestions", {})
    }
