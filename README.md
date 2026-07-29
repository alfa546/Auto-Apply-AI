<p align="center">
  <img src="https://img.shields.io/badge/Auto--Apply--AI-Autonomous_Job_%26_Scholarship_Platform-7C3AED?style=for-the-badge&logo=rocket&logoColor=white" alt="Auto Apply AI Banner" />
</p>

<h1 align="center">🚀 Auto Apply AI</h1>

<p align="center">
  <b>Autonomous Multi-Agent AI Platform for Resume Optimization, Unified Job/Scholarship Search, RAG Semantic Matching, Playwright Browser Auto-Apply, and Gmail Email Tracking.</b>
</p>

<p align="center">
  <a href="#-key-features"><img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Next.js_16-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Python_3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Redis_7-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/ChromaDB-FF6F00?style=flat-square&logo=database&logoColor=white" alt="ChromaDB"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License"></a>
</p>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Infrastructure (Docker Compose)](#1-infrastructure-docker-compose)
  - [Backend Setup (FastAPI)](#2-backend-setup-fastapi)
  - [Frontend Setup (Next.js)](#3-frontend-setup-nextjs)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Testing & Verification](#-testing--verification)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 💡 Overview

**Auto Apply AI** is an enterprise-grade, end-to-end autonomous multi-agent platform designed to streamline and automate the entire career application lifecycle. 

Instead of spending hours manually browsing multiple job portals, tailoring resumes, filling repetitive forms, and tracking application emails, **Auto Apply AI** automates:
1. **Resume Ingestion & Parsing**: Extracts sections, skills, work experience, and calculates ATS compatibility scores.
2. **Unified Opportunity Discovery**: Background scheduler periodically aggregates jobs, internships, scholarships, and hackathons across external platforms.
3. **RAG & Semantic Matching**: Generates vector embeddings for candidate profiles and job listings using `SentenceTransformers` and `ChromaDB` to compute precise compatibility metrics and tailored feedback.
4. **Autonomous Web Application**: Leverages headless Playwright browser automation to auto-fill forms and submit applications.
5. **Smart Email Assistant**: Connects to Gmail API/IMAP to monitor responses, classify status updates (Interviews, Assessments, Rejections), and auto-draft professional follow-up responses.

---

## 🔥 Key Features

### 📄 1. Resume Agent & ATS Analyzer
- **Multi-Format PDF Extraction**: Powered by `pdfplumber` and `PyPDF2`.
- **Structured JSON Schema**: Converts unstructured resumes into validated candidate profiles.
- **ATS Compatibility Scoring**: Evaluates section completeness, formatting, action verbs, and skill density.
- **Semantic Vector Storage**: Embeds candidate skills and experience in `ChromaDB` for instant semantic retrieval.

### 🔍 2. Unified Search Aggregator Engine
- Aggregates **Jobs, Internships, Scholarships, and Hackathons**.
- **Background Daemon Scheduler**: Periodic automated search execution with deduplication.
- Flexible filtering by location, remote status, job type, salary range, and required skills.

### 🎯 3. Semantic RAG Matching Engine
- **Vector Cosine Similarity**: Match percentage calculation between candidate profiles and job requirements.
- **Skill Gap Analysis**: Highlights missing core skills, bonus qualifications, and experience mismatches.
- **Tailored Recommendations**: Generates actionable insights to improve application success rates.

### 🤖 4. Autonomous Application Agent (Playwright)
- **Headless Browser Automation**: Automatically opens job portals, fills personal details, uploads tailored resumes, and navigates multi-step application forms.
- **Live Status Tracking**: Records real-time application states (`APPLIED`, `FAILED`, `MANUAL_ACTION_REQUIRED`).

### 📧 5. Gmail Tracking & Follow-Up Assistant
- **Automated Inbox Scanning**: Connects via OAuth2 / IMAP to monitor employer emails.
- **AI Classification**: Categorizes incoming emails into *Interview Invitation*, *Technical Assessment*, *Rejection*, or *General Inquiry*.
- **Auto-Drafting**: Generates personalized, professional reply drafts directly in your inbox.

### 💻 6. Premium Next.js Dashboard
- Modern, dark-mode inspired UI built with Next.js 16 (App Router), Tailwind CSS v4, and Lucide React icons.
- Real-time application tracking metrics, interactive resume score breakdowns, job discovery feeds, and email management interfaces.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([Candidate / User]) <--> Dashboard[Next.js 16 + Tailwind Dashboard]
    Dashboard <--> REST[FastAPI REST API Server]
    
    subgraph Core Storage & Data Layer
        REST <--> Postgres[(PostgreSQL 16\nRelational DB)]
        REST <--> Redis[(Redis 7\nQueue / Cache)]
        REST <--> VectorDB[(ChromaDB\nVector Embeddings)]
    end

    subgraph Multi-Agent Processing Engine
        REST <--> ResumeAgent[Resume & ATS Parser]
        REST <--> SearchAgent[Search Aggregator Engine]
        REST <--> MatchAgent[RAG Semantic Matcher]
        REST <--> ApplyAgent[Playwright Application Bot]
        REST <--> EmailAgent[Gmail & Email Tracking Engine]
    end

    subgraph External Integrations & Services
        ResumeAgent --> LocalEmbeddings[SentenceTransformer\nall-MiniLM-L6-v2]
        ResumeAgent --> OpenAI[OpenAI API / LLM]
        ApplyAgent --> Playwright[Playwright Headless Browser]
        EmailAgent --> Gmail[Gmail API / OAuth2 / IMAP]
        SearchAgent --> ExternalAPIs[Job Boards / Hackathons / Portals]
    end
```

---

## 🛠️ Tech Stack

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | Next.js 16 (App Router) | React 19, TypeScript, Server & Client Components |
| **Styling** | Tailwind CSS v4 | Responsive modern dark-themed glassmorphic UI |
| **Backend Framework** | FastAPI (Python 3.12+) | Async RESTful API service |
| **Database (Relational)** | PostgreSQL 16 | ORM via SQLAlchemy 2.0 & Alembic Migrations |
| **Vector Database** | ChromaDB | Local / Containerized vector storage for RAG embeddings |
| **Caching & Queues** | Redis 7 | Background task caching and rate limiting |
| **Browser Automation**| Playwright Python | Automated browser form submission and interactions |
| **Embeddings & AI** | SentenceTransformers | `all-MiniLM-L6-v2` local embeddings + OpenAI LLM support |
| **Authentication** | Firebase Admin / JWT | Secure auth verification and user profile management |
| **Containerization** | Docker & Docker Compose | Multi-container orchestration |

---

## 📁 Repository Structure

```
Auto-Apply-AI/
├── backend/                        # FastAPI Backend Application
│   ├── alembic/                    # Database migration scripts
│   ├── src/
│   │   └── app/
│   │       ├── api/                # API Route Handlers
│   │       │   ├── applications.py # Application tracking endpoints
│   │       │   ├── auto_apply.py   # Playwright application triggers
│   │       │   ├── emails.py       # General email endpoints
│   │       │   ├── gmail.py        # Gmail OAuth & inbox tracking
│   │       │   ├── matching.py     # RAG matching & compatibility scores
│   │       │   ├── resumes.py      # Resume parsing & ATS endpoints
│   │       │   ├── search.py       # Aggregator search endpoints
│   │       │   └── users.py        # User profile & settings management
│   │       ├── services/           # Core Business Logic & Agents
│   │       │   ├── application/    # Application submission logic
│   │       │   ├── email/          # Email parsers & drafting
│   │       │   ├── matching/       # RAG ranking algorithms
│   │       │   ├── search/         # Unified opportunity search scrapers
│   │       │   ├── ats_checker.py  # ATS grading & recommendations
│   │       │   ├── embeddings.py   # Vector embedding generators
│   │       │   ├── gmail_client.py # Gmail API integration client
│   │       │   ├── pdf_parser.py   # PDF text extraction utilities
│   │       │   ├── rag_service.py  # Vector search & RAG retriever
│   │       │   └── resume_parser.py# Structured resume extractor
│   │       ├── auth.py             # Authentication middleware
│   │       ├── config.py           # App settings & env configurations
│   │       ├── database.py         # SQLAlchemy DB engine session setup
│   │       ├── main.py             # FastAPI entry point & CORS
│   │       ├── models.py           # Database Models
│   │       └── vector_db.py        # ChromaDB client initialization
│   ├── tests/                      # Pytest suite
│   ├── pyproject.toml              # Backend dependencies (Poetry)
│   ├── requirements.txt            # Pip requirements list
│   └── Dockerfile                  # Backend container build spec
├── frontend/                       # Next.js Frontend Application
│   ├── src/
│   │   └── app/                    # Next.js App Router Pages
│   │       ├── page.tsx            # Main Unified Dashboard UI
│   │       ├── layout.tsx          # Root Layout & Provider Wrapper
│   │       └── globals.css         # Tailwind CSS imports & theme rules
│   ├── package.json                # Frontend dependencies
│   └── next.config.ts              # Next.js configuration
├── docker-compose.yml              # Services orchestration (PostgreSQL, Redis, ChromaDB)
└── README.md                       # Project Documentation
```

---

## ⚡ Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js**: v20.x or higher
- **Python**: v3.12 or higher
- **Docker & Docker Compose**: For running PostgreSQL, Redis, and ChromaDB services
- **Git**: For version control

---

### 1. Infrastructure (Docker Compose)

Start PostgreSQL, Redis, and ChromaDB containers:

```bash
docker compose up -d
```

Verify services are running:
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **ChromaDB**: `localhost:8000`

---

### 2. Backend Setup (FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   # OR using Poetry:
   poetry install
   ```

4. Install Playwright browser dependencies:
   ```bash
   playwright install chromium
   ```

5. Set up your `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

6. Run database migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the FastAPI development server:
   ```bash
   uvicorn src.app.main:app --reload --port 8000
   ```
   The backend API will be available at **`http://localhost:8000`** (Swagger docs at `http://localhost:8000/docs`).

---

### 3. Frontend Setup (Next.js)

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   The web application will be accessible at **`http://localhost:3000`**.

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
# Database Settings
DATABASE_URL=postgresql://postgres:postgres_development_secure_pass@localhost:5432/auto_apply_db

# Redis & Cache Settings
REDIS_URL=redis://localhost:6379/0

# Vector Database
CHROMADB_HOST=localhost
CHROMADB_PORT=8000

# AI Models & LLM Setup
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Gmail Integration (Optional)
GMAIL_CLIENT_ID=your_google_client_id
GMAIL_CLIENT_SECRET=your_google_client_secret
GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/gmail/callback

# Secret Key & Security
SECRET_KEY=super_secret_jwt_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 📡 API Documentation

FastAPI provides an interactive OpenAPI / Swagger UI out of the box at `http://localhost:8000/docs`.

### Core Endpoint Summary

| Category | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **System** | `/api/v1/health` | `GET` | Health check endpoint |
| **Resumes** | `/api/v1/resumes/upload` | `POST` | Upload PDF resume, extract text, run ATS check & embed |
| **Resumes** | `/api/v1/resumes/ats-check` | `POST` | Evaluate ATS compatibility score & get recommendations |
| **Search** | `/api/v1/search` | `GET` | Query aggregated jobs/scholarships/internships |
| **Matching**| `/api/v1/matching/evaluate` | `POST` | Compute vector RAG semantic match between resume & job |
| **Applications**| `/api/v1/applications` | `GET` / `POST` | List and track active user job applications |
| **Auto Apply**| `/api/v1/auto-apply/run` | `POST` | Trigger Playwright browser bot for auto application |
| **Gmail** | `/api/v1/gmail/auth-url` | `GET` | Generate Gmail OAuth authorization URL |
| **Gmail** | `/api/v1/gmail/scan` | `POST` | Scan inbox for employer responses & auto-draft replies |

---

## 🧪 Testing & Verification

Run backend unit and integration tests using `pytest`:

```bash
cd backend
pytest -v
```

---

## 🗺️ Roadmap

- [x] **Phase 1**: Core FastAPI backend architecture, database schemas, and Next.js UI integration.
- [x] **Phase 2**: PDF parser engine, ATS checker, and vector embeddings in ChromaDB.
- [x] **Phase 3**: Multi-board search aggregator & semantic RAG matching engine.
- [x] **Phase 4**: Basic Playwright auto-apply bot execution.
- [x] **Phase 5**: Gmail API OAuth integration & reply drafting.
- [ ] **Phase 6**: Custom Playwright plugins for complex portals (Workday, Greenhouse, Lever).
- [ ] **Phase 7**: Chrome / Firefox Extension for one-click job scraping directly from browser tabs.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="center">
  Crafted with ❤️ by <b>Nouman Sajid</b> for <b>Auto Apply AI</b>
</p>
