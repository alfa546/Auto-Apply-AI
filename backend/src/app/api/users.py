from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.auth import get_current_user
from src.app.storage import storage_service
from src.app.models import User, Profile

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

    return {
        "message": "Resume uploaded successfully.",
        "resume_url": file_url
    }
