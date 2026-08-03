from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from typing import Optional, List, Union
from sqlalchemy.orm import Session
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.storage import storage_service
from src.app.models import User, Profile, UserSettings

from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.resume_parser import parse_resume_text
from src.app.services.ats_checker import evaluate_resume_ats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

class SettingsUpdateRequest(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    custom_api_base: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    adzuna_app_id: Optional[str] = None
    adzuna_app_key: Optional[str] = None
    jooble_api_key: Optional[str] = None
    target_countries: Optional[List[str]] = None

class ProfileUpdateRequest(BaseModel):
    email: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    other_url: Optional[str] = None
    target_roles: Optional[List[str]] = None
    target_countries: Optional[List[str]] = None
    work_mode_preference: Optional[str] = None
    employment_types: Optional[List[str]] = None
    salary_preference: Optional[str] = None
    experience_level: Optional[str] = None
    visa_sponsorship: Optional[Union[bool, str]] = None
    # Also accept string-based visa preference labels from the UI
    visa_sponsorship_str: Optional[str] = None
    daily_job_goal: Optional[int] = None
    daily_internship_goal: Optional[int] = None
    auto_fulfill_enabled: Optional[bool] = None

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
    uid = current_user.get("uid")
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    user = db.query(User).filter(User.id == uid).first()

    # Return masked secret keys for security
    def mask_key(k: Optional[str]):
        if not k or len(k) < 6:
            return ""
        return k[:4] + "••••••••" + k[-4:]

    return {
        "llm_provider": settings.llm_provider or "openai",
        "llm_model": settings.llm_model or "gpt-4o",
        "custom_api_base": settings.custom_api_base or "",
        "openai_api_key": mask_key(settings.openai_api_key),
        "google_client_id": settings.google_client_id or "",
        "google_client_secret": mask_key(settings.google_client_secret),
        "adzuna_app_id": settings.adzuna_app_id or "",
        "adzuna_app_key": mask_key(settings.adzuna_app_key),
        "jooble_api_key": mask_key(settings.jooble_api_key),
        "is_gmail_connected": settings.is_gmail_connected,
        "gmail_email_address": settings.gmail_email_address or "",
        "target_roles": settings.target_roles or [],
        "target_countries": settings.preferred_countries or [],
        "work_mode_preference": settings.work_mode_preference or "Fully Remote (Worldwide)",
        "salary_preference": settings.min_salary_preference or "$90,000 - $130,000 / year",
        "experience_level": settings.experience_level or "Mid-Level (2 - 5 Yrs)",
        "visa_sponsorship": settings.visa_sponsorship_required,
        "daily_job_goal": settings.daily_job_goal,
        "daily_internship_goal": settings.daily_internship_goal,
        "auto_fulfill_enabled": settings.auto_fulfill_enabled,
        "email": user.email if user else "",
        "portfolio_url": profile.portfolio_url if profile else "",
        "github_url": profile.github_url if profile else "",
        "other_url": profile.other_url if profile else "",
        "employment_types": profile.employment_types if profile else []
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
    uid = current_user.get("uid")
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)

    if payload.llm_provider is not None:
        settings.llm_provider = payload.llm_provider
    if payload.llm_model is not None:
        settings.llm_model = payload.llm_model
    if payload.custom_api_base is not None:
        settings.custom_api_base = payload.custom_api_base
    if payload.openai_api_key is not None and "••••••••" not in payload.openai_api_key:
        settings.openai_api_key = payload.openai_api_key
    if payload.google_client_id is not None:
        settings.google_client_id = payload.google_client_id
    if payload.google_client_secret is not None and "••••••••" not in payload.google_client_secret:
        settings.google_client_secret = payload.google_client_secret
    if payload.adzuna_app_id is not None:
        settings.adzuna_app_id = payload.adzuna_app_id
    if payload.adzuna_app_key is not None and "••••••••" not in payload.adzuna_app_key:
        settings.adzuna_app_key = payload.adzuna_app_key
    if payload.jooble_api_key is not None and "••••••••" not in payload.jooble_api_key:
        settings.jooble_api_key = payload.jooble_api_key
    if payload.target_countries is not None:
        settings.preferred_countries = payload.target_countries

    db.commit()
    return {"status": "success", "message": "API keys and integration settings saved successfully!"}

@router.put("/profile")
def update_user_profile(
    payload: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update and save user profile and career preferences.
    """
    uid = current_user.get("uid")
    
    # Ensure User record exists
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid, email=current_user.get("email", f"{uid}@local.com"))
        db.add(user)
        db.commit()
    
    # Update User Profile
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if not profile:
        profile = Profile(user_id=uid)
        db.add(profile)
        
    if payload.portfolio_url is not None:
        profile.portfolio_url = payload.portfolio_url
    if payload.github_url is not None:
        profile.github_url = payload.github_url
    if payload.other_url is not None:
        profile.other_url = payload.other_url
    if payload.employment_types is not None:
        profile.employment_types = payload.employment_types

    # Update User Settings
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        
    if payload.target_roles is not None:
        settings.target_roles = payload.target_roles
    if payload.target_countries is not None:
        settings.preferred_countries = payload.target_countries
    if payload.work_mode_preference is not None:
        settings.work_mode_preference = payload.work_mode_preference
    if payload.salary_preference is not None:
        settings.min_salary_preference = payload.salary_preference
    if payload.experience_level is not None:
        settings.experience_level = payload.experience_level
    # Handle visa sponsorship - the UI sends a string label, but we store a boolean
    if payload.visa_sponsorship is not None:
        if isinstance(payload.visa_sponsorship, str):
            # Map string labels to boolean: any option that mentions "Required" or "Needed" = True
            visa_str = payload.visa_sponsorship.lower()
            settings.visa_sponsorship_required = any(
                keyword in visa_str for keyword in ["required", "needed", "need", "sponsorship"]
            ) and "no visa" not in visa_str and "not required" not in visa_str
        else:
            settings.visa_sponsorship_required = payload.visa_sponsorship
    elif payload.visa_sponsorship_str:
        visa_str = payload.visa_sponsorship_str.lower()
        settings.visa_sponsorship_required = any(
            keyword in visa_str for keyword in ["required", "needed", "need", "sponsorship"]
        ) and "no visa" not in visa_str and "not required" not in visa_str
    if payload.daily_job_goal is not None:
        settings.daily_job_goal = payload.daily_job_goal
    if payload.daily_internship_goal is not None:
        settings.daily_internship_goal = payload.daily_internship_goal
    if payload.auto_fulfill_enabled is not None:
        settings.auto_fulfill_enabled = payload.auto_fulfill_enabled

    db.commit()
    return {"status": "success", "message": "Profile and preferences updated successfully!"}

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
    except Exception as parse_error:
        logger.error(f"Failed to parse resume for user {uid}: {parse_error}", exc_info=True)

    return {
        "message": "Resume uploaded and parsed successfully.",
        "resume_url": file_url
    }
