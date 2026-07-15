from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import Application
from src.app.services.application.pipeline import run_apply_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("")
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by application status, e.g. Matched, Applied, Failed"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all applications for the authenticated user, optionally filtering by status.
    """
    uid = current_user.get("uid")
    query = db.query(Application).filter(Application.user_id == uid)
    
    if status_filter:
        query = query.filter(Application.status == status_filter)
        
    apps = query.order_by(Application.applied_at.desc()).all()
    
    return [
        {
            "id": a.id,
            "title": a.title,
            "company": a.company,
            "opportunity_type": a.opportunity_type,
            "status": a.status,
            "url": a.url,
            "applied_at": a.applied_at,
            "cover_letter": a.cover_letter,
            "notes": a.notes
        }
        for a in apps
    ]

@router.get("/{application_id}")
def get_application_details(
    application_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch details for a specific application record.
    """
    uid = current_user.get("uid")
    app_record = db.query(Application).filter(Application.id == application_id, Application.user_id == uid).first()
    
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application record not found."
        )
        
    return {
        "id": app_record.id,
        "title": app_record.title,
        "company": app_record.company,
        "opportunity_type": app_record.opportunity_type,
        "status": app_record.status,
        "url": app_record.url,
        "applied_at": app_record.applied_at,
        "cover_letter": app_record.cover_letter,
        "notes": app_record.notes
    }

# Background worker wrapper
async def run_apply_background(user_id: str, application_id: int):
    # Setup local DB session for background task thread
    from src.app.database import SessionLocal
    db = SessionLocal()
    try:
        await run_apply_pipeline(db, user_id, application_id)
    except Exception as e:
        logger.error(f"Background apply pipeline crashed: {e}", exc_info=True)
    finally:
        db.close()

@router.post("/{application_id}/apply")
async def trigger_apply(
    application_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers the browser automation form filler pipeline for a matched opportunity.
    Runs asynchronously in the background.
    """
    uid = current_user.get("uid")
    
    # Verify the application exists and belongs to the user
    app_record = db.query(Application).filter(Application.id == application_id, Application.user_id == uid).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application record not found."
        )
        
    if app_record.status in ["Applying", "Applied"]:
        return {
            "status": "ignored",
            "message": f"Application is already in state: {app_record.status}."
        }
        
    # Queue the background task
    background_tasks.add_task(run_apply_background, uid, application_id)
    
    # Instantly transition status in main thread to Applying to prevent double submission triggers
    app_record.status = "Applying"
    db.commit()
    
    return {
        "status": "queued",
        "message": "Playwright form filling agent has been queued in the background."
    }
