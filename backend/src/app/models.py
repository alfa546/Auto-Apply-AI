from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Firebase UID
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    resume_url = Column(String, nullable=True) # Firebase Storage URL
    portfolio_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    other_url = Column(String, nullable=True)
    employment_types = Column(JSON, default=list)
    skills = Column(JSON, default=list) # e.g. ["Python", "FastAPI", "React"]
    experience = Column(JSON, default=list) # List of dicts describing past roles
    education = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    languages = Column(JSON, default=list)
    ats_score = Column(Integer, nullable=True) # Overall ATS score out of 100
    ats_suggestions = Column(JSON, default=dict) # Suggestions for improvement

    user = relationship("User", back_populates="profile")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    # Career Preferences & Target Criteria
    preferred_countries = Column(JSON, default=list) # e.g. ["US", "DE", "UK"]
    target_roles = Column(JSON, default=list) # e.g. ["Backend Developer", "AI Engineer"]
    work_mode_preference = Column(String, default="Remote") # Remote, Hybrid, Onsite
    min_salary_preference = Column(String, nullable=True) # e.g. "$80,000"
    experience_level = Column(String, nullable=True) # Entry, Mid, Senior
    visa_sponsorship_required = Column(Boolean, default=False)
    daily_apply_limit = Column(Integer, default=20)
    daily_job_goal = Column(Integer, default=10)
    daily_internship_goal = Column(Integer, default=5)
    auto_fulfill_enabled = Column(Boolean, default=False)
    
    # 🔑 API Keys & AI Provider Configuration
    llm_provider = Column(String, default="openai") # "openai", "gemini", "deepseek", "groq", "openrouter", "ollama", "custom"
    llm_model = Column(String, default="gpt-4o") # "gpt-4o", "gemini-1.5-pro", "deepseek-chat", "llama-3.1-70b"
    custom_api_base = Column(String, nullable=True) # e.g. "http://localhost:11434/v1" or "https://openrouter.ai/api/v1"
    openai_api_key = Column(String, nullable=True)
    google_client_id = Column(String, nullable=True)
    google_client_secret = Column(String, nullable=True)
    adzuna_app_id = Column(String, nullable=True)
    adzuna_app_key = Column(String, nullable=True)
    jooble_api_key = Column(String, nullable=True)

    # Gmail OAuth & Email Connection Settings
    is_gmail_connected = Column(Boolean, default=False)
    gmail_email_address = Column(String, nullable=True)
    gmail_access_token = Column(String, nullable=True)
    gmail_refresh_token = Column(String, nullable=True)
    smtp_app_password = Column(String, nullable=True)
    
    # Active Search Flags
    search_jobs = Column(Boolean, default=True)
    search_internships = Column(Boolean, default=False)
    search_scholarships = Column(Boolean, default=False)
    search_hackathons = Column(Boolean, default=False)

    user = relationship("User", back_populates="settings")


class JobFound(Base):
    __tablename__ = "jobs_found"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, unique=True, index=True, nullable=False)
    company_email = Column(String, nullable=True) # Extracted HR Email
    salary = Column(String, nullable=True)
    source = Column(String, default="Adzuna") # "Adzuna", "Jooble", "Scraper", "Direct"
    opportunity_type = Column(String, default="job") # "job", "internship", "scholarship", "hackathon"
    match_score = Column(Integer, default=85)
    found_at = Column(DateTime(timezone=True), server_default=func.now())


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    title = Column(String, nullable=False) # e.g. "Software Engineer"
    company = Column(String, nullable=False) # e.g. "Google"
    company_email = Column(String, nullable=True) # Extracted HR contact email
    opportunity_type = Column(String, default="job") # "job", "internship", "scholarship", "hackathon"
    status = Column(String, default="Applied") # "Applied", "Interview Pending", "Rejected", "Sent via Gmail", "Accepted"
    url = Column(String, nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    cover_letter = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="applications")


class EmailInteraction(Base):
    __tablename__ = "email_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    
    sender_email = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    gmail_message_id = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="Sent")


class CustomCoverLetter(Base):
    __tablename__ = "custom_cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id = Column(Integer, ForeignKey("jobs_found.id", ondelete="CASCADE"), nullable=True)
    
    content = Column(String, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
