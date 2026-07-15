import logging
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase App
firebase_initialized = False
if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PROJECT_ID != "your-firebase-project-id":
    try:
        firebase_admin.get_app()
        firebase_initialized = True
    except ValueError:
        try:
            firebase_admin.initialize_app(options={
                'projectId': settings.FIREBASE_PROJECT_ID,
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET
            })
            firebase_initialized = True
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase Admin: {e}. Falling back to Mock Auth.")

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(token_creds: HTTPAuthorizationCredentials = Security(security_scheme)):
    """
    FastAPI dependency to extract and verify the Firebase ID token.
    Falls back to a mock user context if Firebase is not initialized or if a mock token is passed.
    """
    if not token_creds:
        if not firebase_initialized:
            # Under development mode (no Firebase), fallback to default mock user
            return {"uid": "mock-user-123", "email": "mock-user-123@example.com"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
        )
    
    token = token_creds.credentials

    # If it is a mock token (e.g. "dev-mock-123") or Firebase is not active
    if not firebase_initialized or token.startswith("dev-mock-"):
        uid = token.replace("dev-mock-", "") if token.startswith("dev-mock-") else "mock-user-123"
        return {"uid": uid, "email": f"{uid}@example.com"}

    try:
        decoded_token = auth.verify_id_token(token)
        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )
