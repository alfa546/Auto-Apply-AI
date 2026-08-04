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
from src.app.services.auto_apply.runner import auto_apply_runner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-apply", tags=["Direct Email Auto Apply"])

class ApplyRequest(BaseModel):
    job_id: int
    custom_cover_letter: Optional[str] = None

class AutoApplyBatchRequest(BaseModel):
    job_count: Optional[int] = 10
    internship_count: Optional[int] = 3

def get_uid_and_email(user_context):
    if isinstance(user_context, dict):
        uid = user_context.get("uid", "")
        email = user_context.get("email", "")
    else:
        uid = str(getattr(user_context, "id", ""))
        email = getattr(user_context, "email", "")
    return uid, email

def build_cover_letter_with_links(cover_letter: str, profile: Profile) -> str:
    """
    Appends GitHub, LinkedIn, and Portfolio links to the cover letter signature block.
    """
    links = []
    if profile:
        if profile.github_url:
            links.append(f"GitHub: {profile.github_url}")
        if profile.portfolio_url:
            links.append(f"Portfolio: {profile.portfolio_url}")
        if profile.other_url:
            links.append(f"LinkedIn: {profile.other_url}")

    if not links:
        return cover_letter

    # Append links section before the signature
    links_block = "\n\n" + "\n".join(links)
    # Insert before "Sincerely," or "Best regards," or at the end
    import re
    signature_match = re.search(r"\n(Sincerely|Best regards|Regards|Yours truly)[,\s]", cover_letter, re.IGNORECASE)
    if signature_match:
        insert_pos = signature_match.start()
        return cover_letter[:insert_pos] + links_block + cover_letter[insert_pos:]
    else:
        return cover_letter + links_block

def prepare_application_data(
    db: Session,
    uid: str,
    user_email: str,
    job: JobFound,
    user_settings: UserSettings,
    profile: Profile,
    custom_cover_letter: Optional[str] = None
) -> dict:
    """
    Shared helper to prepare all email application data (recipient, subject, cover letter, cv path).
    Used by both the preview endpoint and the send endpoint.
    """
    recipient_email = job.company_email
    if not recipient_email:
        recipient_email = f"careers@{job.company.lower().replace(' ', '')}.com"

    sender_email = user_settings.gmail_email_address or user_email
    if not sender_email:
        raise HTTPException(
            status_code=400,
            detail="No sender email address configured. Please connect your Gmail account in Settings."
        )

    raw_resume_url = profile.resume_url if profile and profile.resume_url else None
    cv_path = resolve_resume_local_path(raw_resume_url) if raw_resume_url else None
    if cv_path:
        logger.info(f"Resume resolved to local path: {cv_path}")
    else:
        logger.warning(f"Could not resolve resume path from: {raw_resume_url}")

    subject = f"Application for {job.title} - {user_email}"

    if custom_cover_letter:
        cover_letter = custom_cover_letter
    else:
        try:
            # Pass user's saved LLM settings (API key, provider, model) if available
            user_api_key = user_settings.openai_api_key
            user_provider = user_settings.llm_provider
            user_model = user_settings.llm_model
            user_custom_base = user_settings.custom_api_base

            # Temporarily override global settings for this request
            import src.app.config as config_module
            _saved_openai = config_module.settings.OPENAI_API_KEY
            _saved_gemini = config_module.settings.GEMINI_API_KEY
            if user_api_key:
                if user_provider == "gemini" or user_api_key.startswith("AIzaSy"):
                    config_module.settings.GEMINI_API_KEY = user_api_key
                else:
                    config_module.settings.OPENAI_API_KEY = user_api_key

            try:
                cover_letter = generate_custom_cover_letter(
                    candidate_name=user_email.split("@")[0],
                    job_title=job.title,
                    company=job.company,
                    skills=profile.skills if profile else [],
                    job_description=job.description or job.title
                )
            finally:
                # Restore original settings
                config_module.settings.OPENAI_API_KEY = _saved_openai
                config_module.settings.GEMINI_API_KEY = _saved_gemini
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

    # Append GitHub / LinkedIn / Portfolio links to the cover letter
    cover_letter = build_cover_letter_with_links(cover_letter, profile)

    return {
        "recipient_email": recipient_email,
        "sender_email": sender_email,
        "subject": subject,
        "cover_letter": cover_letter,
        "cv_path": cv_path,
        "job_title": job.title,
        "company": job.company
    }

@router.post("/preview")
def preview_application_email(
    payload: ApplyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generates a preview of the email application WITHOUT sending it.
    Returns recipient, subject, cover letter, and attachment info for user review.
    """
    uid, user_email = get_uid_and_email(current_user)

    # 1. Check Job Details
    job = db.query(JobFound).filter(JobFound.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # 2. Check User Gmail Connection
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not user_settings or not user_settings.is_gmail_connected:
        raise HTTPException(
            status_code=400,
            detail="Gmail is not connected. Please connect your Gmail account in Settings before applying."
        )

    # 3. Fetch User Profile
    profile = db.query(Profile).filter(Profile.user_id == uid).first()

    # 4. Prepare all data (no sending)
    data = prepare_application_data(
        db=db,
        uid=uid,
        user_email=user_email,
        job=job,
        user_settings=user_settings,
        profile=profile,
        custom_cover_letter=payload.custom_cover_letter
    )

    return {
        "success": True,
        "preview": {
            "job_title": data["job_title"],
            "company": data["company"],
            "recipient_email": data["recipient_email"],
            "sender_email": data["sender_email"],
            "subject": data["subject"],
            "cover_letter": data["cover_letter"],
            "has_resume_attachment": bool(data["cv_path"]),
            "resume_filename": os.path.basename(data["cv_path"]) if data["cv_path"] else None
        }
    }

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

    # 2. Check User Gmail Connection
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not user_settings or not user_settings.is_gmail_connected:
        raise HTTPException(
            status_code=400,
            detail="Gmail is not connected. Please connect your Gmail account in Settings before applying."
        )

    # 3. Fetch User Profile
    profile = db.query(Profile).filter(Profile.user_id == uid).first()

    # 4. Prepare all data
    data = prepare_application_data(
        db=db,
        uid=uid,
        user_email=user_email,
        job=job,
        user_settings=user_settings,
        profile=profile,
        custom_cover_letter=payload.custom_cover_letter
    )

    recipient_email = data["recipient_email"]
    sender_email = data["sender_email"]
    subject = data["subject"]
    cover_letter = data["cover_letter"]
    cv_path = data["cv_path"]

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

@router.post("/start")
def start_auto_apply_batch(
    payload: AutoApplyBatchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Starts a fully automated batch auto-apply.
    Applies to up to 10 jobs and up to 3 internships without user review.
    Runs in the background until targets are met or stopped.
    """
    uid, user_email = get_uid_and_email(current_user)

    # Check Gmail connection
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not user_settings or not user_settings.is_gmail_connected:
        raise HTTPException(
            status_code=400,
            detail="Gmail is not connected. Please connect your Gmail account in Settings before applying."
        )

    # Check resume/profile exists
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if not profile or not profile.resume_url:
        raise HTTPException(
            status_code=400,
            detail="No resume found. Please upload your resume in Profile before starting auto-apply."
        )

    # Validate and start batch
    try:
        result = auto_apply_runner.start_batch(
            db=db,
            uid=uid,
            user_email=user_email,
            job_count=payload.job_count or 10,
            internship_count=payload.internship_count or 3
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
def get_auto_apply_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the current status of the auto-apply batch runner for the user.
    """
    uid, _ = get_uid_and_email(current_user)
    return auto_apply_runner.get_status(uid)

@router.post("/stop")
def stop_auto_apply_batch(
    current_user: dict = Depends(get_current_user)
):
    """
    Stops the running auto-apply batch for the user.
    """
    uid, _ = get_uid_and_email(current_user)
    return auto_apply_runner.stop_batch(uid)

@router.post("/dismiss")
def dismiss_auto_apply_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Dismisses/clears the completed, stopped, or failed auto-apply status for the user.
    """
    uid, _ = get_uid_and_email(current_user)
    return auto_apply_runner.dismiss_batch(uid)
