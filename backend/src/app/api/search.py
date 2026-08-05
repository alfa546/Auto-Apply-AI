from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.models import JobFound, User
from src.app.services.search.aggregator import SearchAggregator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

class TriggerSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="The search query, e.g. 'Python Developer'. If empty, Preferences-guided search is triggered.")
    country: Optional[str] = Field(None, description="Country code, e.g. 'us', 'gb'")

@router.post("/trigger")
async def trigger_search(
    payload: TriggerSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers the Search Aggregator pipeline to scan for new opportunities based on user preferences and resume skills.
    """
    aggregator = SearchAggregator()
    try:
        user_id = current_user.id
        
        if payload.query:
            new_jobs = await aggregator.run_aggregation(
                db=db,
                query=payload.query,
                country=payload.country or "us",
                user_id=user_id
            )
        else:
            new_jobs = await aggregator.run_preferences_guided_search(
                db=db,
                user_id=user_id
            )
            
        return {
            "status": "success",
            "message": f"Preferences-guided search completed. Discovered {new_jobs} new opportunities.",
            "new_opportunities_found": new_jobs
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search aggregation trigger failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run opportunity search: {str(e)}"
        )

@router.get("/opportunities")
def get_opportunities(
    opportunity_type: Optional[str] = Query(None, description="Filter by type: job, internship, scholarship, hackathon"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    title: Optional[str] = Query(None, description="Filter by job title (partial match)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the list of parsed opportunities found by the aggregator pipeline.
    """
    query = db.query(JobFound)
    
    if opportunity_type:
        query = query.filter(JobFound.opportunity_type == opportunity_type)
    if company:
        query = query.filter(JobFound.company.ilike(f"%{company}%"))
    if title:
        query = query.filter(JobFound.title.ilike(f"%{title}%"))

    # Order by discovery date descending
    total = query.count()
    opportunities = query.order_by(JobFound.found_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": o.id,
                "title": o.title,
                "company": o.company,
                "location": o.location,
                "country": o.country,
                "description": o.description,
                "url": o.url,
                "company_email": o.company_email,
                "extracted_emails": o.extracted_emails or [],
                "salary": o.salary,
                "source": o.source,
                "opportunity_type": o.opportunity_type,
                "match_score": o.match_score,
                "found_at": o.found_at
            }
            for o in opportunities
        ]
    }
