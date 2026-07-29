from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.storage import storage_service
from src.app.models import User, Profile, UserSettings

from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.resume_parser import parse_resume_text
from src.app.services.ats_checker import evaluate_resume_ats
from src.app.services.embeddings import generate_and_store_resume_embeddings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

class SettingsUpdateRequest(BaseModel):
    openai_api_key: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    adzuna_app_id: Optional[str] = None
    adzuna_app_key: Optional[str] = None
    jooble_api_key: Optional[str] = None
    target_countries: Optional[List[str]] = None

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch the authenticated user's database record or initialize a new record if first time.
    """
    uid = current_user.get("uid")
    email = current_user.get("email")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "profile": {
            "resume_url": user.profile.resume_url if user.profile else None,
            "skills": user.profile.skills if user.profile else [],
            "ats_score": user.profile.ats_score if user.profile else None
        } if user.profile else None
    }

@router.get("/settings")
def get_user_settings(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch user API keys and integration credentials.
    """
    uid = current_user.get("uid", "dev-mock-matcher_test_uid")
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    # Return masked secret keys for security
    def mask_key(k: Optional[str]):
        if not k or len(k) < 6:
            return ""
        return k[:4] + "••••••••" + k[-4:]

    return {
        "openai_api_key": mask_key(settings.openai_api_key),
        "google_client_id": settings.google_client_id or "",
        "google_client_secret": mask_key(settings.google_client_secret),
        "adzuna_app_id": settings.adzuna_app_id or "",
        "adzuna_app_key": mask_key(settings.adzuna_app_key),
        "jooble_api_key": mask_key(settings.jooble_api_key),
        "is_gmail_connected": settings.is_gmail_connected,
        "gmail_email_address": settings.gmail_email_address or ""
    }

@router.put("/settings")
def update_user_settings(
    payload: SettingsUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update and save user API keys and integration credentials.
    """
    uid = current_user.get("uid", "dev-mock-matcher_test_uid")
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)

    if payload.openai_api_key is not None and not payload.openai_api_key.startswith("••"):
        settings.openai_api_key = payload.openai_api_key
    if payload.google_client_id is not None:
        settings.google_client_id = payload.google_client_id
    if payload.google_client_secret is not None and not payload.google_client_secret.startswith("••"):
        settings.google_client_secret = payload.google_client_secret
    if payload.adzuna_app_id is not None:
        settings.adzuna_app_id = payload.adzuna_app_id
    if payload.adzuna_app_key is not None and not payload.adzuna_app_key.startswith("••"):
        settings.adzuna_app_key = payload.adzuna_app_key
    if payload.jooble_api_key is not None and not payload.jooble_api_key.startswith("••"):
        settings.jooble_api_key = payload.jooble_api_key
    if payload.target_countries is not None:
        settings.preferred_countries = payload.target_countries

    db.commit()
    return {"status": "success", "message": "API keys and integration settings saved successfully!"}

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload user's resume PDF, save to storage, and link the URL to the user's profile.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files are accepted."
        )

    content = await file.read()
    file_url = storage_service.upload(content, file.filename)
    
    uid = current_user.get("uid")
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid, email=current_user.get("email"))
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if not profile:
        profile = Profile(user_id=uid, resume_url=file_url)
        db.add(profile)
    else:
        profile.resume_url = file_url
        
    db.commit()
    db.refresh(profile)

    try:
        raw_text = extract_text_from_pdf(content)
        profile_data = parse_resume_text(raw_text)
        ats_results = evaluate_resume_ats(profile_data)
        
        profile.skills = profile_data.get("skills", [])
        profile.experience = profile_data.get("experience", [])
        profile.education = profile_data.get("education", [])
        profile.projects = profile_data.get("projects", [])
        profile.languages = profile_data.get("languages", [])
        profile.ats_score = ats_results.get("ats_score")
        profile.ats_suggestions = ats_results.get("ats_suggestions")
        
        db.commit()
        db.refresh(profile)
        
        generate_and_store_resume_embeddings(uid, profile_data)
    except Exception as parse_error:
        logger.error(f"Failed to parse or index resume for user {uid}: {parse_error}", exc_info=True)

    return {
        "message": "Resume uploaded and parsed successfully.",
        "resume_url": file_url
    }
