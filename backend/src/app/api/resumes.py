from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import User, Profile
from src.app.services.ats_checker import evaluate_resume_ats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])

class ATSCheckRequest(BaseModel):
    target_role: Optional[str] = Field(None, description="The job title or role to evaluate against")
    job_description: Optional[str] = Field(None, description="Full job description text to run semantic keywords matching")

@router.get("/profile")
def get_resume_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the current authenticated user's structured resume profile, ATS score, and recommendations.
    """
    uid = current_user.get("uid")
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume profile found for this user. Please upload a resume first."
        )
        
    return {
        "resume_url": profile.resume_url,
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
    uid = current_user.get("uid")
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume profile found. Please upload a resume first."
        )
        
    profile_data = {
        "skills": profile.skills,
        "experience": profile.experience,
        "education": profile.education,
        "projects": profile.projects,
        "languages": profile.languages
    }
    
    # Evaluate ATS score with target_role
    target = payload.target_role or (payload.job_description[:100] if payload.job_description else None)
    ats_results = evaluate_resume_ats(profile_data, target_role=target)
    
    # Optionally update the user's base score/suggestions in the database
    profile.ats_score = ats_results.get("ats_score")
    profile.ats_suggestions = ats_results.get("ats_suggestions")
    db.commit()
    db.refresh(profile)
    
    return ats_results
