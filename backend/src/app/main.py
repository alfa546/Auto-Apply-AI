from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.app.api.users import router as users_router
from src.app.api.resumes import router as resumes_router

app = FastAPI(
    title="Auto Apply AI API",
    description="Backend API services supporting multi-agent automated job/scholarship application platform",
    version="0.1.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists and mount it to serve uploaded assets
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(users_router, prefix="/api/v1")
app.include_router(resumes_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Auto Apply AI API",
        "version": "0.1.0"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

