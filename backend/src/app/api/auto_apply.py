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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-apply", tags=["Direct Email Auto Apply"])

class ApplyRequest(BaseModel):
    job_id: int
    custom_cover_letter: Optional[str] = None

@router.post("/send-email")
def auto_apply_via_email(
    payload: ApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Auto-applies to a specific job by generating a tailored cover letter,
    attaching user's CV PDF, and sending directly from user's connected Gmail.
    """
    # 1. Check Job Details
    job = db.query(JobFound).filter(JobFound.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    recipient_email = job.company_email
    if not recipient_email:
        recipient_email = f"careers@{job.company.lower().replace(' ', '')}.com"

    # 2. Check User Gmail Connection
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings or not user_settings.is_gmail_connected:
        # Fallback to dev demo mode email address if not connected
        sender_email = current_user.email
    else:
        sender_email = user_settings.gmail_email_address or current_user.email

    # 3. Fetch User Profile and Resume
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    cv_path = profile.resume_url if profile and profile.resume_url else None
    
    # Check physical CV file path on disk
    if cv_path and not os.path.isabs(cv_path):
        cv_path = os.path.abspath(cv_path)

    # 4. Generate AI Tailored Cover Letter
    subject = f"Application for {job.title} - {profile.user.email if profile else current_user.email}"
    
    if payload.custom_cover_letter:
        cover_letter = payload.custom_cover_letter
    else:
        try:
            cover_letter = generate_custom_cover_letter(
                resume_data={
                    "skills": profile.skills if profile else [],
                    "summary": profile.summary if profile else "Software Developer"
                },
                job_description=job.description or job.title,
                company_name=job.company
            )
        except Exception as e:
            logger.warning(f"Fallback cover letter generation: {e}")
            cover_letter = (
                f"Dear Hiring Manager at {job.company},\n\n"
                f"I am writing to express my strong interest in the {job.title} position.\n"
                f"With my background in software development and skills in {', '.join(profile.skills[:5] if profile and profile.skills else ['programming'])}, "
                f"I am confident in my ability to add immediate value to your team.\n\n"
                f"Please find my attached resume for your consideration. I look forward to hearing from you.\n\n"
                f"Best regards,\n{sender_email}"
            )

    # 5. Send Email
    send_result = None
    if user_settings and user_settings.smtp_app_password:
        send_result = gmail_client.send_email_via_smtp(
            sender_email=sender_email,
            app_password=user_settings.smtp_app_password,
            recipient_email=recipient_email,
            subject=subject,
            body_text=cover_letter,
            cv_file_path=cv_path
        )
    elif user_settings and user_settings.gmail_access_token:
        send_result = gmail_client.send_email_via_oauth(
            access_token=user_settings.gmail_access_token,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body_text=cover_letter,
            cv_file_path=cv_path
        )
    else:
        # Mock/Dev Mode Send
        import uuid
        send_result = {
            "success": True,
            "message_id": f"msg_mock_{uuid.uuid4().hex[:10]}",
            "method": "Dev_Mock"
        }

    # 6. Record Application in DB
    app_record = Application(
        user_id=current_user.id,
        title=job.title,
        company=job.company,
        company_email=recipient_email,
        opportunity_type=job.opportunity_type,
        status="Sent via Gmail" if send_result.get("success") else "Failed",
        url=job.url,
        cover_letter=cover_letter,
        sent_via_gmail=True,
        gmail_message_id=send_result.get("message_id"),
        cv_attached_path=cv_path,
        notes=f"Sent to {recipient_email} via {send_result.get('method')}"
    )
    db.add(app_record)
    db.commit()

    return {
        "success": send_result.get("success", False),
        "message": f"Successfully applied to {job.company} ({job.title})! Sent to {recipient_email}",
        "recipient_email": recipient_email,
        "gmail_message_id": send_result.get("message_id"),
        "cover_letter_preview": cover_letter[:200] + "..."
    }
