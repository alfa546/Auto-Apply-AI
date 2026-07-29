from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Firebase Auth UID
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    email_interactions = relationship("EmailInteraction", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Extracted data & User Links
    resume_url = Column(String, nullable=True)
    raw_resume_text = Column(String, nullable=True) # Full text extracted for RAG
    portfolio_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    target_roles = Column(JSON, default=[]) # Target job titles (e.g. ["Python Developer", "Full Stack"])
    summary = Column(String, nullable=True)
    skills = Column(JSON, default=[]) # List of extracted skills
    experience = Column(JSON, default=[]) # Extracted experience list of dicts
    education = Column(JSON, default=[]) # Extracted education details list of dicts
    projects = Column(JSON, default=[]) # Extracted projects list of dicts
    languages = Column(JSON, default=[]) # Languages spoken
    ats_score = Column(Integer, nullable=True)
    ats_suggestions = Column(JSON, default={})
    rag_collection_id = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    preferred_countries = Column(JSON, default=[]) # e.g. ["Germany", "UK"]
    min_salary = Column(Numeric(12, 2), nullable=True)
    max_salary = Column(Numeric(12, 2), nullable=True)
    remote_preference = Column(String, default="both") # "remote", "onsite", "both"
    visa_sponsorship_required = Column(Boolean, default=False)
    daily_apply_limit = Column(Integer, default=20)
    
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
    
    # Gmail Proof Fields
    sent_via_gmail = Column(Boolean, default=False)
    gmail_message_id = Column(String, nullable=True)
    cv_attached_path = Column(String, nullable=True)
    
    user = relationship("User", back_populates="applications")
    custom_cover_letter = relationship("CustomCoverLetter", back_populates="application", uselist=False, cascade="all, delete-orphan")
    email_interactions = relationship("EmailInteraction", back_populates="application", cascade="all, delete-orphan")


class JobFound(Base):
    __tablename__ = "jobs_found"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    company_email = Column(String, nullable=True) # Extracted company hiring email
    extracted_emails = Column(JSON, default=[]) # List of emails found in job description
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, unique=True, index=True, nullable=False)
    salary = Column(String, nullable=True)
    opportunity_type = Column(String, default="job") # "job", "internship", "scholarship", "hackathon"
    skills_required = Column(JSON, default=[])
    match_score = Column(Numeric(5, 2), default=0.0) # Percentage match based on RAG
    source = Column(String, default="aggregator")
    posted_at = Column(DateTime(timezone=True), nullable=True)
    found_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(JSON, default={})


class CustomCoverLetter(Base):
    __tablename__ = "custom_cover_letters"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="custom_cover_letter")


class EmailInteraction(Base):
    __tablename__ = "email_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), index=True, nullable=True)
    sender = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(String, nullable=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    classification = Column(String, nullable=True) # e.g. "Interview Invite", "Rejection", "Confirmation"
    response_draft = Column(String, nullable=True)
    status = Column(String, default="Pending Review") # e.g. "Pending Review", "Approved", "Sent", "Dismissed"

    user = relationship("User", back_populates="email_interactions")
    application = relationship("Application", back_populates="email_interactions")

