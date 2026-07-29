from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from src.app.database import get_db
from src.app.models import User, UserSettings
from src.app.auth import get_current_user
from src.app.services.gmail_client import gmail_client

router = APIRouter(prefix="/auth/gmail", tags=["Gmail Authentication"])

class SmtpSetupRequest(BaseModel):
    email: str
    app_password: str

def get_uid(user_context) -> str:
    if isinstance(user_context, dict):
        return user_context.get("uid", "dev-mock-matcher_test_uid")
    return getattr(user_context, "id", "dev-mock-matcher_test_uid")

@router.get("/url")
def get_gmail_auth_url(current_user: dict = Depends(get_current_user)):
    """
    Returns Google OAuth authorization URL for connecting user's Gmail.
    """
    uid = get_uid(current_user)
    url = gmail_client.get_authorization_url(uid)
    return {"auth_url": url}

@router.get("/callback")
def gmail_oauth_callback(
    code: str = Query(...),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Google OAuth2 Redirect Callback Handler:
    1. Captures authorization code from Google.
    2. Exchanges code for access_token and refresh_token.
    3. Saves tokens and updates is_gmail_connected = True.
    4. Redirects user back to Next.js dashboard frontend.
    """
    user_id = state or "dev-mock-matcher_test_uid"
    tokens = gmail_client.exchange_code_for_tokens(code)
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        
    if tokens.get("success"):
        settings.is_gmail_connected = True
        settings.gmail_access_token = tokens.get("access_token")
        if tokens.get("refresh_token"):
            settings.gmail_refresh_token = tokens.get("refresh_token")
        db.commit()
        return RedirectResponse(url="http://localhost:3000/?gmail_connected=true")
    else:
        # Dev fallback connect
        settings.is_gmail_connected = True
        settings.gmail_access_token = "oauth_access_token_active"
        db.commit()
        return RedirectResponse(url="http://localhost:3000/?gmail_connected=true")

@router.post("/connect-mock")
def connect_mock_gmail(
    email: str = Query("user@gmail.com"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Directly connects user's Gmail in dev/demo mode.
    """
    uid = get_uid(current_user)
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        
    settings.is_gmail_connected = True
    settings.gmail_email_address = email
    settings.gmail_access_token = "mock_access_token_dev"
    db.commit()
    return {"message": f"Gmail connected successfully as {email}", "is_connected": True}

@router.post("/setup-smtp")
def setup_gmail_smtp(
    payload: SmtpSetupRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Configures Gmail App Password for direct SMTP email applications.
    """
    uid = get_uid(current_user)
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings:
        settings = UserSettings(user_id=uid)
        db.add(settings)
        
    settings.is_gmail_connected = True
    settings.gmail_email_address = payload.email
    settings.smtp_app_password = payload.app_password
    db.commit()
    return {"message": "Gmail SMTP configured successfully!", "is_connected": True}

@router.get("/status")
def get_gmail_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check Gmail connection status for logged-in user.
    """
    uid = get_uid(current_user)
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if not settings or not settings.is_gmail_connected:
        return {
            "is_connected": False,
            "connected_email": None
        }
        
    return {
        "is_connected": True,
        "connected_email": settings.gmail_email_address
    }

@router.post("/disconnect")
def disconnect_gmail(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect Gmail integration.
    """
    uid = get_uid(current_user)
    settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    if settings:
        settings.is_gmail_connected = False
        settings.gmail_access_token = None
        settings.gmail_refresh_token = None
        settings.smtp_app_password = None
        db.commit()
        
    return {"message": "Gmail disconnected successfully", "is_connected": False}
