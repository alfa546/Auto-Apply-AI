from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.services.matching.pipeline import run_matching_pipeline
from src.app.services.matching.matcher import MatchingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matching", tags=["matching"])

@router.post("/run")
async def execute_matching(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes the matching pipeline on all discovered opportunities,
    populating the user's application pipeline with Matched results.
    """
    uid = current_user.get("uid")
    try:
        new_matches = await run_matching_pipeline(db=db, user_id=uid)
        return {
            "status": "success",
            "message": f"Matching evaluation completed. Queued {new_matches} new matches.",
            "new_matches_queued": new_matches
        }
    except Exception as e:
        logger.error(f"Failed to run matching pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute matching pipeline: {str(e)}"
        )

@router.get("/evaluate/{job_id}")
async def evaluate_single_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluate and return detailed matching scores and reasons for a specific job opportunity.
    """
    uid = current_user.get("uid")
    engine = MatchingEngine()
    try:
        result = await engine.evaluate_job_match(db=db, user_id=uid, job_id=job_id)
        return result
    except Exception as e:
        logger.error(f"Single job matching evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate job matching: {str(e)}"
        )
