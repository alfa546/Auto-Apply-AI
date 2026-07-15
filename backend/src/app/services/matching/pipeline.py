import logging
from sqlalchemy.orm import Session
from src.app.models import JobFound, Application
from src.app.services.matching.matcher import MatchingEngine

logger = logging.getLogger(__name__)

async def run_matching_pipeline(db: Session, user_id: str) -> int:
    """
    Evaluates new discovered opportunities against user profile constraints and matching logic.
    Creates 'Application' records for high-scoring matches.
    Returns the count of newly queued applications.
    """
    logger.info(f"Running matching pipeline for user: {user_id}")
    
    # 1. Fetch user's existing application URLs to avoid duplicate matching
    existing_urls = {app.url for app in db.query(Application).filter(Application.user_id == user_id).all() if app.url}
    
    # 2. Fetch all found opportunities
    opportunities = db.query(JobFound).all()
    
    # Filter out opportunities the user has already applied/matched to
    unprocessed_jobs = [job for job in opportunities if job.url not in existing_urls]
    
    if not unprocessed_jobs:
        logger.info(f"No new unprocessed jobs found for user: {user_id}")
        return 0

    logger.info(f"Found {len(unprocessed_jobs)} unprocessed jobs to evaluate.")
    
    engine = MatchingEngine()
    matched_count = 0

    for job in unprocessed_jobs:
        try:
            eval_result = await engine.evaluate_job_match(db, user_id, job.id)
            if eval_result.get("is_match"):
                # Create a matched application queue item
                new_app = Application(
                    user_id=user_id,
                    title=job.title,
                    company=job.company,
                    opportunity_type=job.opportunity_type,
                    status="Matched",
                    url=job.url,
                    notes=" || ".join(eval_result.get("reasons", []))
                )
                db.add(new_app)
                matched_count += 1
                logger.info(f"Job Match Found: '{job.title}' at '{job.company}' with score {eval_result.get('score'):.1%}")
        except Exception as e:
            logger.error(f"Error evaluating job match {job.id} for user {user_id}: {e}", exc_info=True)

    if matched_count > 0:
        db.commit()

    logger.info(f"Matching pipeline completed for user {user_id}. Queued {matched_count} matches.")
    return matched_count
