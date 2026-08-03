import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.models import User, Profile, UserSettings, Application, JobFound
from src.app.auth import get_current_user
from src.app.services.gmail_client import gmail_client
from src.app.services.llm_client import generate_custom_cover_letter
from src.app.services.application.pipeline import resolve_resume_local_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-apply", tags=["Direct Email Auto Apply"])

class ApplyRequest(BaseModel):
    job_id: int
    custom_cover_letter: Optional[str] = None

def get_uid_and_email(user_context):
    if isinstance(user_context, dict):
        uid = user_context.get("uid", "")
        email = user_context.get("email", "")
    else:
        uid = str(getattr(user_context, "id", ""))
        email = getattr(user_context, "email", "")
    return uid, email

@router.post("/send-email")
def auto_apply_via_email(
    payload: ApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Auto-applies to a specific job by generating a tailored cover letter,
    attaching user's CV PDF, and sending directly from user's connected Gmail.
    """
    uid, user_email = get_uid_and_email(current_user)

    # 1. Check Job Details
    job = db.query(JobFound).filter(JobFound.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    recipient_email = job.company_email
    if not recipient_email:
        recipient_email = f"careers@{job.company.lower().replace(' ', '')}.com"

    # 2. Check User Gmail Connection
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not user_settings or not user_settings.is_gmail_connected:
        raise HTTPException(
            status_code=400,
            detail="Gmail is not connected. Please connect your Gmail account in Settings before applying."
        )
    
    # Determine sender email - use connected Gmail address or fall back to user email
    sender_email = user_settings.gmail_email_address or user_email
    if not sender_email:
        raise HTTPException(
            status_code=400,
            detail="No sender email address configured. Please connect your Gmail account in Settings."
        )

    # 3. Fetch User Profile and Resume
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    raw_resume_url = profile.resume_url if profile and profile.resume_url else None
    cv_path = resolve_resume_local_path(raw_resume_url) if raw_resume_url else None
    if cv_path:
        logger.info(f"Resume resolved to local path: {cv_path}")
    else:
        logger.warning(f"Could not resolve resume path from: {raw_resume_url}")

    # 4. Generate AI Tailored Cover Letter
    subject = f"Application for {job.title} - {user_email}"
    
    if payload.custom_cover_letter:
        cover_letter = payload.custom_cover_letter
    else:
        try:
            cover_letter = generate_custom_cover_letter(
                candidate_name=user_email.split("@")[0],
                job_title=job.title,
                company=job.company,
                skills=profile.skills if profile else [],
                job_description=job.description or job.title
            )
        except Exception as e:
            logger.warning(f"Fallback cover letter generation: {e}")
            skills_str = ', '.join(profile.skills[:5]) if profile and profile.skills else 'software development'
            cover_letter = (
                f"Dear Hiring Manager at {job.company},\n\n"
                f"I am writing to express my strong interest in the {job.title} position.\n"
                f"With my background in software development and skills in {skills_str}, "
                f"I am confident in my ability to add immediate value to your team.\n\n"
                f"Please find my attached resume for your consideration. I look forward to hearing from you.\n\n"
                f"Best regards,\n{sender_email}"
            )

    # 5. Send Email
    send_result = None
    if user_settings.smtp_app_password:
        send_result = gmail_client.send_email_via_smtp(
            sender_email=sender_email,
            app_password=user_settings.smtp_app_password,
            recipient_email=recipient_email,
            subject=subject,
            body_text=cover_letter,
            cv_file_path=cv_path
        )
    elif user_settings.gmail_access_token:
        send_result = gmail_client.send_email_via_oauth(
            access_token=user_settings.gmail_access_token,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body_text=cover_letter,
            cv_file_path=cv_path,
            refresh_token=user_settings.gmail_refresh_token,
            client_id=user_settings.google_client_id,
            client_secret=user_settings.google_client_secret
        )
        
        # Save new access token if returned (even on failure, to avoid re-authentication)
        if send_result.get("new_access_token"):
            user_settings.gmail_access_token = send_result.get("new_access_token")
    else:
        raise HTTPException(
            status_code=400,
            detail="Gmail is connected but no sending method is configured. Please set up either Google OAuth or SMTP App Password in Settings."
        )

    # 6. Record Application in DB
    app_record = Application(
        user_id=uid,
        title=job.title,
        company=job.company,
        company_email=recipient_email,
        opportunity_type=job.opportunity_type or "job",
        status="Sent via Gmail" if send_result.get("success") else "Failed",
        url=job.url,
        cover_letter=cover_letter,
        notes=f"Sent to {recipient_email} via {send_result.get('method')}",
        gmail_message_id=send_result.get("message_id")
    )
    db.add(app_record)
    db.commit()

    success = send_result.get("success", False)
    message = (
        f"Successfully applied to {job.company} ({job.title})! Sent to {recipient_email}"
        if success
        else f"Failed to apply to {job.company} ({job.title}). Error: {send_result.get('error', 'Unknown error')}"
    )
    
    return {
        "success": success,
        "message": message,
        "recipient_email": recipient_email,
        "gmail_message_id": send_result.get("message_id"),
        "error": send_result.get("error") if not success else None,
        "cover_letter_preview": cover_letter[:200] + "..."
    }
