import os
import re
import uuid
import logging
import httpx
import tempfile
from sqlalchemy.orm import Session
from src.app.models import Application, User, Profile, JobFound
from src.app.services.application.cover_letter import generate_cover_letter
from src.app.services.application.form_filler import FormFillerService
from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.notification import NotificationService

logger = logging.getLogger(__name__)

def extract_contact_info(raw_text: str, default_email: str) -> dict:
    """
    Scans raw resume text for contact details (Phone, LinkedIn, GitHub).
    """
    info = {
        "name": "Candidate Name",
        "email": default_email,
        "phone": "555-0199",
        "linkedin": "https://linkedin.com/in/candidate",
        "github": "https://github.com/candidate"
    }

    # Extract Name (often the first non-empty line of the resume)
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    if lines:
        # Check if first line looks like a name (short, no email chars)
        first_line = lines[0]
        if len(first_line) < 40 and not any(c in first_line for c in ["@", "http", ".com"]):
            info["name"] = first_line

    # Extract Phone
    phone_match = re.search(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", raw_text)
    if phone_match:
        info["phone"] = phone_match.group(0)

    # Extract LinkedIn
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", raw_text)
    if linkedin_match:
        url = linkedin_match.group(0)
        info["linkedin"] = url if url.startswith("http") else f"https://{url}"

    # Extract GitHub
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", raw_text)
    if github_match:
        url = github_match.group(0)
        info["github"] = url if url.startswith("http") else f"https://{url}"

    return info

def resolve_resume_local_path(resume_url: str) -> str:
    """
    Resolves the resume URL into a absolute local file path.
    Downloads the file to a temp location if it resides on a remote server.
    """
    if not resume_url:
        return None

    # Handle local upload folder URLs
    if resume_url.startswith("/uploads/"):
        # Remove leading slash and resolve relative to current backend execution path
        local_path = resume_url.lstrip("/")
        if os.path.exists(local_path):
            return os.path.abspath(local_path)
        
        # Also try resolving relative to the backend directory (in case cwd differs)
        backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        alt_path = os.path.join(backend_root, local_path)
        if os.path.exists(alt_path):
            return os.path.abspath(alt_path)

    if os.path.exists(resume_url):
        return os.path.abspath(resume_url)

    # Handle remote HTTP download
    try:
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"resume_{uuid.uuid4()}.pdf")
        
        with httpx.Client() as client:
            response = client.get(resume_url, timeout=10.0)
            if response.status_code == 200:
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Downloaded remote resume file to temp path: {temp_path}")
                return temp_path
    except Exception as e:
        logger.error(f"Failed to resolve and download resume file: {e}")
        
    return None

async def run_apply_pipeline(db: Session, user_id: str, application_id: int) -> dict:
    """
    Drives the complete application sequence:
    1. Grabs matching job metadata.
    2. Generates hyper-tailored cover letter content.
    3. Parses contacts dynamically from resume.
    4. Navigates, fills out form, and uploads materials via Playwright.
    5. Saves page screenshots and updates database states.
    """
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise ValueError("Application record not found.")

    # Transition state to Applying
    app_record.status = "Applying"
    db.commit()

    logger.info(f"Starting application pipeline for {app_record.title} at {app_record.company}")

    try:
        # Fetch profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not profile or not profile.resume_url:
            raise Exception("User has not uploaded a resume.")

        # 1. Resolve resume file path
        resume_path = resolve_resume_local_path(profile.resume_url)
        if not resume_path or not os.path.exists(resume_path):
            raise Exception(f"Failed to find or download resume file at: {profile.resume_url}")

        # 2. Extract raw text from resume for contact information scanning
        with open(resume_path, "rb") as f:
            pdf_bytes = f.read()
        raw_text = extract_text_from_pdf(pdf_bytes)
        
        candidate_info = extract_contact_info(raw_text, user.email)
        
        # 3. Find job details (description) to tailor the cover letter
        job_desc = "Software developer opportunity."
        job = db.query(JobFound).filter(JobFound.url == app_record.url).first()
        if job and job.description:
            job_desc = job.description

        # 4. Generate cover letter
        profile_data = {
            "skills": profile.skills,
            "experience": profile.experience,
            "education": profile.education,
        }
        cover_letter_content = generate_cover_letter(
            profile_data=profile_data,
            job_title=app_record.title,
            company=app_record.company,
            job_description=job_desc
        )
        
        # Update cover letter in application record
        app_record.cover_letter = cover_letter_content
        db.commit()

        # 5. Execute browser automation form filler
        filler = FormFillerService()
        fill_result = await filler.auto_fill_application(
            application_url=app_record.url,
            candidate_info=candidate_info,
            resume_path=resume_path,
            cover_letter_content=cover_letter_content
        )

        # 6. Process automation outputs
        if fill_result.get("success"):
            app_record.status = "Applied"
            app_record.notes = f"Successfully applied. Screenshot: {fill_result.get('screenshot_path')}"
            logger.info(f"Successfully applied to {app_record.title} at {app_record.company}")
            
            msg = f"<b>Auto Apply AI Alert</b>\n\nSuccessfully applied to: <b>{app_record.title}</b> at <b>{app_record.company}</b>\nURL: {app_record.url}\nScreenshot: {fill_result.get('screenshot_path')}"
            await NotificationService.send_notification(msg)
        else:
            app_record.status = "Failed"
            app_record.notes = f"Failed to apply: {fill_result.get('error_message')}. Screenshot: {fill_result.get('screenshot_path')}"
            logger.error(f"Application submission failed for {app_record.title}: {fill_result.get('error_message')}")
            
            msg = f"<b>Auto Apply AI Alert</b>\n\nFailed to apply to: <b>{app_record.title}</b> at <b>{app_record.company}</b>\nError: {fill_result.get('error_message')}"
            await NotificationService.send_notification(msg)

        db.commit()
        return fill_result
    except Exception as pipeline_error:
        error_msg = str(pipeline_error)
        logger.error(f"Failed to execute apply pipeline: {error_msg}", exc_info=True)
        app_record.status = "Failed"
        app_record.notes = f"Pipeline execution error: {error_msg}"
        db.commit()
        
        msg = f"<b>Auto Apply AI Alert</b>\n\nPipeline execution failed for: <b>{app_record.title}</b> at <b>{app_record.company}</b>\nPipeline Error: {error_msg}"
        await NotificationService.send_notification(msg)
        return {"success": False, "screenshot_path": None, "error_message": error_msg}
