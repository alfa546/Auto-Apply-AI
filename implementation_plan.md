# Implementation Plan - Auto Apply AI (Phase-by-Phase Roadmap)

This document outlines a phased engineering roadmap to build **Auto Apply AI**, a fully automated multi-agent system that parses resumes, searches for jobs/internships/scholarships/hackathons, evaluates compatibility, automatically applies via browser automation/APIs, and manages notifications/follow-up email drafts.

We will break the development into 10 structured, independent milestones. We will only execute milestones as approved by the user.

---

## Technical Stack & Architecture

```mermaid
graph TD
    Client[Next.js + Tailwind + ShadCN Dashboard] <--> API[FastAPI Backend]
    API <--> Postgres[(PostgreSQL DB)]
    API <--> Redis[(Redis Queue / Cache)]
    API <--> VectorDB[(Vector DB: Qdrant/Chroma)]
    API <--> LangGraph[LangGraph Orchestrator]
    
    subgraph Agents [LangGraph Multi-Agent System]
        RA[Resume Parser & ATS Agent]
        SA[Search Agent: Jobs/Scholarships/Hackathons]
        MA[Matching & Ranking Agent]
        AA[Application & Playwright Agent]
        EA[Email Monitoring & Draft Agent]
    end

    subgraph External [External Services]
        Firebase[Firebase Auth & Storage]
        Gmail[Gmail API / IMAP]
        Playwright[Playwright Browser Automation]
        JobAPIs[Job Boards & Portals APIs]
    end

    LangGraph --> RA
    LangGraph --> SA
    LangGraph --> MA
    LangGraph --> AA
    LangGraph --> EA

    AA --> Playwright
    SA --> JobAPIs
    EA --> Gmail
    API <--> Firebase
```

---

## 10-Step Implementation Roadmap

### Step 1: Project Initialization & Directory Structure
Set up the monorepo structure, initializing the FastAPI backend, Next.js frontend, and standard environment/configuration structures.
*   **Backend setup**: Poetry or Pipenv with `fastapi`, `uvicorn`, `pydantic`.
*   **Frontend setup**: Next.js with React, Tailwind CSS, and Lucide React icons.
*   **Config**: Shared `.env.example` templates, Docker Compose files for PostgreSQL, Redis, and Vector DB.

### Step 2: Database Schema Design & Migrations (PostgreSQL + Firestore + Vector DB)
Define structured relational schemas for application tracking, settings, and logs, alongside vector configurations for semantic matching.
*   **PostgreSQL (SQLAlchemy/Alembic)**: Schemas for `users`, `profiles`, `applications` (Google, Microsoft, etc., with status logs), `jobs_found`, `custom_cover_letters`, `email_interactions`.
*   **Vector DB (Chroma/Qdrant)**: Setup collection schemas for embedding resume chunks and job descriptions.
*   **Firestore & Storage**: Models for real-time notifications and PDF resume file storage configurations.

### Step 3: Authentication & File Storage (Firebase Integration)
Implement secure authentication and user asset uploads.
*   **Authentication**: Firebase Admin SDK integration in FastAPI to verify JWT tokens issued by Next.js Firebase Auth.
*   **Storage**: Firebase Storage (or local S3-compatible service for development) to upload and retrieve resume PDFs and certificates.

### Step 4: Resume Agent (PDF Parsing, Embeddings & ATS Analysis)
Build the ingestion pipeline that parses uploaded PDFs and translates them into structured JSON profiles and embeddings.
*   **PDF Parser**: Integration with `PyPDF2` / `pdfplumber` / LLM parsing to extract structured sections (Education, Skills, Experience, Projects).
*   **ATS Checker**: LLM prompt engine to score resumes against standard industries and identify missing skills.
*   **Embedding Pipeline**: Generate embeddings of resume parts using SentenceTransformers / OpenAI Embeddings and index them in the Vector DB.

### Step 5: Search Agent (APIs, Scraping & Aggregator Pipeline)
Create a scheduled engine that regularly queries open APIs and scrapes job/scholarship listings.
*   **APIs**: Integrations with Adzuna, Jooble, and scraping scripts for Google Careers, Greenhouse, Lever, Ashby.
*   **Scholarship/Hackathons Crawlers**: RSS feeds and web scraper modules targeting top scholarship and hackathon lists.
*   **Scheduler**: APScheduler or Celery Beat worker executing hourly.

### Step 6: Matching Agent (Semantic Matching & Score Thresholding)
Build the decision-making engine that compares extracted candidate profiles against incoming jobs/opportunities.
*   **Vector Search**: Semantic similarity queries between job descriptions and resume profiles.
*   **Constraint Checking**: Hard filtering on preferred countries, salary range, remote vs. onsite, visa sponsorship, and daily apply limits.
*   **Ranking logic**: Output matching percentage (e.g. 92%) and queue for auto-applying if above a threshold (e.g., >80%).

### Step 7: Application Agent (Playwright Browser Automation & Cover Letter Generator)
Implement the core automation that fills out forms and uploads candidate materials.
*   **Playwright Engine**: Scripts to log in, navigate, and dynamically fill out standard application forms (Name, Email, Phone, LinkedIn, GitHub, Resume upload, Custom questions).
*   **Cover Letter Generator**: Dynamic prompt engine to generate context-aware, hyper-tailored cover letters for the specific job description and company.
*   **Status Reporter**: Save screenshot artifacts and update application state in DB.

### Step 8: Email Agent (Inbox Monitoring & Automatic Drafting)
Automate check-ins on applicant mailboxes to capture interviewer responses or requests.
*   **Gmail Integration**: IMAP / Gmail API listener to watch for replies from applied domains.
*   **Classification Engine**: LLM classification of incoming emails (e.g., Interview Invite, Rejection, Action Required: Transcript/References).
*   **Draft Writer**: Automatically draft responses (e.g. providing references, confirming time slots) and notify the user via DB/Dashboard.

### Step 9: User Dashboard (Next.js Frontend)
Construct a premium, dark-themed responsive dashboard for checking stats and logs.
*   **Views**: Home (daily target progress bar, status metrics), Applications list, Statistics (Acceptance rate, Interview vs Rejected chart), AI Suggestions page, Notifications panel.
*   **Real-time updates**: Setup WebSocket or polling to fetch application logs.

### Step 10: System Integration, Notification Agents & End-to-End Testing
Add real-time push alerts and verify the system works under high concurrency.
*   **Notification Agent**: Integrations with Discord Webhooks / Telegram Bot API / Firebase Cloud Messaging.
*   **End-to-End Validation**: Mock job portals testing complete cycle (Resume Upload -> Match -> Generate Assets -> Playwright Apply -> Status Updated).

---

## Verification Plan

### Automated Tests
*   `pytest tests/test_resume_parser.py`: Verify parsing correctness on sample resumes.
*   `pytest tests/test_match_agent.py`: Confirm matching thresholds filter jobs correctly.
*   `pytest tests/test_playwright_forms.py`: Run local mock-server application forms to ensure Playwright reliably fills out details.

### Manual Verification
*   Visual inspection of parsed profiles on Dashboard UI.
*   Review generated cover letters for quality.
*   Check email draft folder for correctly formatted responses.
