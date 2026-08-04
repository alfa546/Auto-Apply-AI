import time
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import os

from src.app.config import settings
from src.app.api.auth import router as auth_router
from src.app.api.users import router as users_router
from src.app.api.resumes import router as resumes_router
from src.app.api.search import router as search_router
from src.app.api.matching import router as matching_router
from src.app.api.applications import router as applications_router
from src.app.api.emails import router as emails_router
from src.app.api.gmail import router as gmail_router
from src.app.api.auto_apply import router as auto_apply_router
from src.app.api.admin import router as admin_router
from src.app.services.search.scheduler import start_search_scheduler, stop_search_scheduler
from src.app.database import get_db
from src.app.models import User, Plan, Subscription, SubscriptionStatus

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Auto Apply AI API",
    description="Backend API services supporting multi-agent automated job/scholarship application platform",
    version="0.2.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add trusted host middleware (adjust allowed hosts as needed)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify exact domains
)

# Startup and shutdown event hooks for the search aggregator background daemon
@app.on_event("startup")
async def startup_event():
    try:
        await start_search_scheduler()
    except Exception as e:
        print(f"⚠️ Search scheduler failed to start (non-fatal): {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await stop_search_scheduler()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists and mount it to serve uploaded assets
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(matching_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(emails_router, prefix="/api/v1")
app.include_router(gmail_router, prefix="/api/v1")
app.include_router(auto_apply_router, prefix="/api/v1")

# Include admin router (admin-only endpoints)
app.include_router(admin_router)

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Auto Apply AI API",
        "version": "0.2.0"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}