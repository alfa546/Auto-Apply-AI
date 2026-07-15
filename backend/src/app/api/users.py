from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import logging
from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.storage import storage_service
from src.app.models import User, Profile

from src.app.services.pdf_parser import extract_text_from_pdf
from src.app.services.resume_parser import parse_resume_text
from src.app.services.ats_checker import evaluate_resume_ats
from src.app.services.embeddings import generate_and_store_resume_embeddings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetch the authenticated user's database record or initialize a new record if first time.
    """
    uid = current_user.get("uid")
    email = current_user.get("email")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        # Create a new user record upon first login/token verification
        user = User(id=uid, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "profile": {
            "resume_url": user.profile.resume_url if user.profile else None,
            "skills": user.profile.skills if user.profile else [],
            "ats_score": user.profile.ats_score if user.profile else None
        } if user.profile else None
    }


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload user's resume PDF, save to storage, and link the URL to the user's profile.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files are accepted."
        )

    # Read file content
    content = await file.read()
    
    # Upload to storage
    file_url = storage_service.upload(content, file.filename)
    
    uid = current_user.get("uid")
    
    # Ensure user exists in database
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        user = User(id=uid, email=current_user.get("email"))
        db.add(user)
        db.commit()
        db.refresh(user)

    # Retrieve or create profile
    profile = db.query(Profile).filter(Profile.user_id == uid).first()
    if not profile:
        profile = Profile(user_id=uid, resume_url=file_url)
        db.add(profile)
    else:
        profile.resume_url = file_url
        
    db.commit()
    db.refresh(profile)

    # Run the parsing and indexing pipeline
    try:
        raw_text = extract_text_from_pdf(content)
        profile_data = parse_resume_text(raw_text)
        ats_results = evaluate_resume_ats(profile_data)
        
        # Save parsed data to DB profile
        profile.skills = profile_data.get("skills", [])
        profile.experience = profile_data.get("experience", [])
        profile.education = profile_data.get("education", [])
        profile.projects = profile_data.get("projects", [])
        profile.languages = profile_data.get("languages", [])
        profile.ats_score = ats_results.get("ats_score")
        profile.ats_suggestions = ats_results.get("ats_suggestions")
        
        db.commit()
        db.refresh(profile)
        
        # Generate embeddings and store in ChromaDB
        generate_and_store_resume_embeddings(uid, profile_data)
    except Exception as parse_error:
        logger.error(f"Failed to parse or index resume for user {uid}: {parse_error}", exc_info=True)

    return {
        "message": "Resume uploaded and parsed successfully.",
        "resume_url": file_url
    }
