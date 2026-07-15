from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import EmailInteraction, User, Profile
from src.app.services.email.watcher import EmailInboxWatcher
from src.app.services.email.classifier import classify_email
from src.app.services.email.draft_writer import generate_draft_reply
from src.app.services.application.pipeline import extract_contact_info
from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.application.pipeline import resolve_resume_local_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["emails"])

async def run_email_check_pipeline(db: Session, user_id: str):
    """
    Background pipeline that checks inbox, filters by user applications,
    classifies received emails, and drafts professional responses.
    """
    logger.info(f"Triggering email check pipeline for user: {user_id}")
    watcher = EmailInboxWatcher()
    
    # 1. Fetch matching unseen emails
    email_items = await watcher.check_inbox(db, user_id)
    if not email_items:
        logger.info("No new matching emails found.")
        return
        
    # 2. Retrieve candidate profile data for reply tailoring
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    candidate_profile = {"name": "Candidate", "skills": []}
    if profile:
        candidate_profile["skills"] = profile.skills or []
        # Try to resolve candidate name from resume file
        resume_path = resolve_resume_local_path(profile.resume_url)
        if resume_path:
            try:
                with open(resume_path, "rb") as f:
                    pdf_bytes = f.read()
                raw_text = extract_text_from_pdf(pdf_bytes)
                contact = extract_contact_info(raw_text, user.email)
                candidate_profile["name"] = contact.get("name", "Candidate")
            except Exception:
                pass
                
    # 3. Process each email
    for item in email_items:
        # Check for duplicates (same sender and subject)
        existing = db.query(EmailInteraction).filter(
            EmailInteraction.user_id == user_id,
            EmailInteraction.sender == item["sender"],
            EmailInteraction.subject == item["subject"]
        ).first()
        
        if existing:
            continue
            
        # Classify
        classification = classify_email(item["subject"], item["body"])
        
        # Draft Response
        draft = generate_draft_reply(
            classification=classification,
            sender=item["sender"],
            subject=item["subject"],
            body=item["body"],
            candidate_profile=candidate_profile
        )
        
        # Save Interaction
        interaction = EmailInteraction(
            user_id=user_id,
            application_id=item["application_id"],
            sender=item["sender"],
            recipient=item["recipient"],
            subject=item["subject"],
            body=item["body"],
            classification=classification,
            response_draft=draft,
            status="Pending Review"
        )
        db.add(interaction)
        
    db.commit()

@router.get("/drafts")
def list_drafts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all email interactions and their auto-generated response drafts.
    """
    uid = current_user.get("uid")
    interactions = db.query(EmailInteraction).filter(
        EmailInteraction.user_id == uid
    ).order_by(EmailInteraction.received_at.desc()).all()
    
    return [
        {
            "id": i.id,
            "application_id": i.application_id,
            "sender": i.sender,
            "recipient": i.recipient,
            "subject": i.subject,
            "body": i.body,
            "received_at": i.received_at,
            "classification": i.classification,
            "response_draft": i.response_draft,
            "status": i.status
        }
        for i in interactions
    ]

@router.post("/check")
async def trigger_check(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually triggers email checking in the background.
    """
    uid = current_user.get("uid")
    
    # We run database operations on background worker threads
    # To prevent thread race, we pass task parameters
    async def task_wrapper():
        from src.app.database import SessionLocal
        bg_db = SessionLocal()
        try:
            await run_email_check_pipeline(bg_db, uid)
        finally:
            bg_db.close()

    background_tasks.add_task(task_wrapper)
    return {"status": "success", "message": "Email inbox check has been queued."}

@router.post("/drafts/{draft_id}/approve")
def approve_draft(
    draft_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve an auto-generated draft, updating its status to 'Approved' (ready to send).
    """
    uid = current_user.get("uid")
    interaction = db.query(EmailInteraction).filter(
        EmailInteraction.id == draft_id,
        EmailInteraction.user_id == uid
    ).first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )
        
    interaction.status = "Approved"
    db.commit()
    
    return {"status": "success", "message": "Draft marked as Approved."}

@router.delete("/drafts/{draft_id}")
def discard_draft(
    draft_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismiss or discard a draft reply.
    """
    uid = current_user.get("uid")
    interaction = db.query(EmailInteraction).filter(
        EmailInteraction.id == draft_id,
        EmailInteraction.user_id == uid
    ).first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )
        
    interaction.status = "Dismissed"
    db.commit()
    
    return {"status": "success", "message": "Draft marked as Dismissed."}
