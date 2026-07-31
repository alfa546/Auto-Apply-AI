import logging
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.config import settings

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = "local_dev_secret_key_auto_apply_ai_2026"
ALGORITHM = "HS256"

async def get_current_user(token_creds: HTTPAuthorizationCredentials = Security(security_scheme)):
    """
    FastAPI dependency to extract and verify the JWT token.
    """
    if not token_creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
        )
    
    token = token_creds.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "uid": payload.get("uid"),
            "email": payload.get("sub")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
