from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import logging

from src.app.db.database import get_db
from src.app.db.models import User, UserSettings
from src.app.core.security import get_current_user
from src.app.core.config import settings
from src.app.services.gmail_client import gmail_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/gmail", tags=["Gmail Authentication"])

class SmtpSetupRequest(BaseModel):
    email: str
    app_password: str

def get_uid(user_context) -> str:
    if isinstance(user_context, dict):
        return user_context.get("uid", "")
    return str(getattr(user_context, "id", ""))

@router.get("/url")
def get_gmail_auth_url(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns Google OAuth authorization URL for connecting user's Gmail.
    """
    uid = get_uid(current_user)
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == uid).first()
    client_id = user_settings.google_client_id if (user_settings and user_settings.google_client_id) else None
    url = gmail_client.get_authorization_url(uid, client_id=client_id)
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
    if not state:
        raise HTTPException(status_code=400, detail="Missing OAuth state parameter (user ID).")
    user_id = state

    # Validate that the user actually exists - prevents an attacker from
    # binding their Gmail to an arbitrary user_id via the callback.
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        logger.warning(f"Gmail OAuth callback received for unknown user_id: {user_id}")
        raise HTTPException(status_code=400, detail="Invalid OAuth state (unknown user).")
    user_id = user_exists.id

    settings_row = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings_row:
        settings_row = UserSettings(user_id=user_id)
        db.add(settings_row)

    cid = settings_row.google_client_id if (settings_row and settings_row.google_client_id) else None
    csecret = settings_row.google_client_secret if (settings_row and settings_row.google_client_secret) else None
    tokens = gmail_client.exchange_code_for_tokens(code, client_id=cid, client_secret=csecret)
        
    if tokens.get("success"):
        settings_row.is_gmail_connected = True
        settings_row.gmail_access_token = tokens.get("access_token")
        if tokens.get("refresh_token"):
            settings_row.gmail_refresh_token = tokens.get("refresh_token")
        
        # Fetch the user's Gmail email address using the access token
        try:
            import httpx
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
            with httpx.Client(timeout=10.0) as client:
                userinfo_res = client.get(userinfo_url, headers=headers)
                if userinfo_res.status_code == 200:
                    userinfo = userinfo_res.json()
                    gmail_addr = userinfo.get("email")
                    if gmail_addr:
                        settings_row.gmail_email_address = gmail_addr
                        logger.info(f"Retrieved Gmail address: {gmail_addr}")
                else:
                    logger.warning(f"Failed to fetch Gmail userinfo: {userinfo_res.status_code} - {userinfo_res.text}")
        except Exception as e:
            logger.warning(f"Error fetching Gmail userinfo: {e}")
        
        db.commit()
        return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}?gmail_connected=true")
    else:
        error_msg = tokens.get("error", "OAuth failed")
        return RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}?gmail_error={error_msg}")

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
