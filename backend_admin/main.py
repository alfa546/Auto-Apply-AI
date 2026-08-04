"""
Admin Portal Backend - Separate FastAPI application for admin operations
Runs on port 8001
"""
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from src.app.config import Settings
from src.app.database import get_db, engine, Base
from src.app.models import User, UserRole
from src.app.auth import get_current_user

# Create admin app
admin_app = FastAPI(
    title="Auto Apply AI - Admin Portal API",
    description="Admin-only API for managing users, subscriptions, API vault, and system monitoring",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Admin-specific CORS (only admin frontend)
admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://admin.yourplatform.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin security scheme
security_scheme = HTTPBearer(auto_error=False)

# Admin settings (separate from main app)
settings = Settings()

logger = logging.getLogger(__name__)


# Startup event - create tables if needed
@admin_app.on_event("startup")
async def startup_event():
    """
    Initialize admin backend.
    In production, use Alembic migrations instead.
    """
    try:
        # Import all models to ensure they're registered
        from src.app import models
        Base.metadata.create_all(bind=engine)
        logger.info("Admin backend database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize admin database: {e}")


# Health check
@admin_app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "admin-backend",
        "version": "0.1.0"
    }


# Root endpoint
@admin_app.get("/")
async def root():
    return {
        "message": "Auto Apply AI - Admin Portal API",
        "version": "0.1.0",
        "docs": "/docs"
    }


# Import and include admin routers
from src.app.api.admin import vault as vault_router

# Include admin routers
admin_app.include_router(vault_router.router, prefix="/api/v1/admin", tags=["admin"])


# Admin-only dependency
async def get_admin_user(
    token_creds: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify admin token and return admin user.
    Must have ADMIN or SUPER_ADMIN role.
    """
    if not token_creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )
    
    token = token_creds.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        uid = payload.get("uid")
        email = payload.get("sub")
        
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
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
    
    # Fetch user
    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Check admin role
    if user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(admin_app, host="0.0.0.0", port=8001)