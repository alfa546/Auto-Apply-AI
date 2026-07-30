<p align="center">
  <img src="https://img.shields.io/badge/Auto--Apply--AI-Autonomous_Job_%26_Scholarship_Platform-7C3AED?style=for-the-badge&logo=rocket&logoColor=white" alt="Auto Apply AI Banner" />
</p>

<h1 align="center">🚀 Auto Apply AI</h1>

<p align="center">
  <b>Autonomous Multi-Agent AI Platform for Resume Optimization, Multi-Country Target Search, RAG Semantic Matching, Playwright Browser Auto-Apply, and Gmail Email Tracking.</b>
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
  - [Connecting Gmail on Localhost](#4-connecting-gmail-on-localhost)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Testing & Verification](#-testing--verification)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 💡 Overview

**Auto Apply AI** is an enterprise-grade, end-to-end autonomous multi-agent platform designed to streamline and automate the entire career application lifecycle. 

Instead of spending hours manually browsing multiple job portals, tailoring resumes, filling repetitive forms, and tracking application emails, **Auto Apply AI** automates:
1. **Resume Ingestion & RAG Parsing**: Extracts sections, skills, work experience, and calculates authentic ATS compatibility scores (0-100%).
2. **Interactive Searchable Country Box**: Search and add up to **10 target destination countries** (e.g., United States 🇺🇸, Canada 🇨🇦, UK 🇬🇧, Germany 🇩🇪, UAE 🇦🇪, Japan 🇯🇵) with live removable tag badges.
3. **Multi-Agent RAG Search Aggregator**: Combines candidate RAG vector skills from ChromaDB + user target roles + selected target countries to execute targeted multi-country opportunity scraping.
4. **Daily Application Goals & Automation Targets**: Allows users to set custom daily job and internship application targets with live percentage completion bars.
5. **Gmail Email Auto-Apply Proofs**: Sends candidate CVs directly to company hiring emails with message IDs delivered to the user's Gmail "Sent" folder, complete with **Today / Monthly / Yearly** period history filters.

---

## 🔥 Key Features

### 🔍 1. Interactive Country Autocomplete Search Box (1-10 Countries)
- **Real-Time Autocomplete Dropdown**: Search from 50+ global destination countries by typing in the search box.
- **Dynamic Tag Badges**: Selected countries appear below the search box as removable badges (`✓ Country ✕`).
- **Strict 1-10 Limit Enforcement**: Allows candidates to target multiple international markets simultaneously with toast notifications for boundary limits.

### 🌐 2. International Career & Preference Center
- **Work Mode / Remote Policies**: `Fully Remote (Worldwide)`, `Remote (Americas)`, `Remote (EMEA)`, `Remote (APAC)`, `Hybrid`, `On-site`.
- **Compensation & Experience**: Standardized USD salary bands ($40,000 - $180,000+ / yr) and experience tiers (Entry-Level to Staff/Principal).
- **Visa & Relocation Settings**: Filter roles based on visa sponsorship and relocation support needs.

### 🎯 3. Multi-Agent RAG Search & Match Engine
- **RAG-Guided Search**: Merges vector embeddings of candidate CV skills from ChromaDB + user preferences to discover high-relevance opportunities.
- **Semantic Compatibility Scoring**: Computes composite match percentages (e.g. 96.5% Match) based on cosine similarity and technical skill density.
- **Hiring HR Email Extractor**: Automatically parses company HR contact emails (`careers@company.com`, `hr@...`) for direct email application delivery.

### 🎯 4. Daily Application Goals & Progress Tracker
- **Customizable Targets**: Set independent daily application targets for Jobs and Internships.
- **Live Progress Bar**: Visual completion percentage tracker (`Today's Goal Progress: X / Y Applications`).

### 📧 5. Gmail Proofs & History Hub (Today / Monthly / Yearly)
- **Direct Gmail Integration**: Connects via Google OAuth2 or 16-character App Password (SMTP).
- **Time-Period Filters**: Filter applications by **Today** (24 hours), **Monthly** (current month), **Yearly** (2026), or **All**.
- **Delivery Proof**: Displays Gmail Message IDs verifying that applications are sent from the candidate's personal Gmail account.

### 📄 6. Authentic ATS Resume Scoring & RAG Deep Hub
- **ATS Metrics Dashboard**: Evaluates formatting, skill density, impact action verbs, and section completeness.
- **Actionable Recommendations**: Generates missing keyword suggestions and formatting feedback.

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
        REST <--> SearchAgent[RAG & Country Guided Search Aggregator]
        REST <--> MatchAgent[RAG Semantic Matcher]
        REST <--> ApplyAgent[Playwright Application Bot]
        REST <--> EmailAgent[Gmail & Email Tracking Engine]
    end

    subgraph External Integrations & Services
        ResumeAgent --> LocalEmbeddings[SentenceTransformer\nall-MiniLM-L6-v2]
        ResumeAgent --> OpenAI[OpenAI API / LLM]
        ApplyAgent --> Playwright[Playwright Headless Browser]
        EmailAgent --> Gmail[Gmail API / OAuth2 / SMTP]
        SearchAgent --> ExternalAPIs[Multi-Country Job Scrapers / Adzuna / Jooble / RSS]
    end
```

---

## 🛠️ Tech Stack

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | Next.js 16 (App Router) | React 19, TypeScript, Client-side State & Components |
| **Styling** | Tailwind CSS v4 | Responsive dark-themed UI with glassmorphism |
| **Backend Framework** | FastAPI (Python 3.12+) | Asynchronous RESTful API services |
| **Database (Relational)** | PostgreSQL 16 | ORM via SQLAlchemy 2.0 & Alembic Migrations |
| **Vector Database** | ChromaDB | Vector storage for candidate RAG resume embeddings |
| **Caching & Queues** | Redis 7 | Background task queues and rate limiting |
| **Browser Automation**| Playwright Python | Automated browser form submission and interactions |
| **Embeddings & AI** | SentenceTransformers | `all-MiniLM-L6-v2` local embeddings + OpenAI LLM support |
| **Authentication** | Firebase Admin / JWT / SMTP | Secure auth verification and email credentials |
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
│   │       │   ├── search.py       # RAG & Country search endpoints
│   │       │   └── users.py        # User profile & settings management
│   │       ├── services/           # Core Business Logic & Agents
│   │       │   ├── application/    # Application submission logic
│   │       │   ├── email/          # Email parsers & drafting
│   │       │   ├── matching/       # RAG ranking algorithms
│   │       │   ├── search/         # Search Aggregator with RAG + Preferences
│   │       │   ├── ats_checker.py  # ATS grading & recommendations
│   │       │   ├── embeddings.py   # Vector embedding generators
│   │       │   ├── gmail_client.py # Gmail API / SMTP integration client
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
│   │       ├── page.tsx            # Unified Dashboard (Jobs -> Proofs -> Profile/RAG)
│   │       ├── layout.tsx          # Root Layout & Provider Wrapper
│   │       └── globals.css         # Tailwind CSS imports & theme rules
│   ├── package.json                # Frontend dependencies
│   └── next.config.ts              # Next.js configuration
├── docker-compose.yml              # Services orchestration (PostgreSQL, Redis, ChromaDB)
└── README.md                       # Main Project Documentation
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

### 4. Connecting Gmail on Localhost (2 Easy Methods)

When running the application locally on localhost (`http://localhost:3000`), a candidate can connect their Gmail account so that the AI Agent can send application emails with custom cover letters and PDF CVs directly to company HR emails.

#### Method A: Gmail App Password (SMTP) - Fast 1-Minute Setup (Recommended for Localhost)
No Google Cloud Console configuration required!
1. Go to your **Google Account** (`https://myaccount.google.com/`).
2. Go to **Security** → Enable **2-Step Verification** (if not already enabled).
3. Search for **App Passwords** or visit `https://myaccount.google.com/apppasswords`.
4. Create a new App Password (e.g., App Name: `Auto-Apply AI`).
5. Google will generate a **16-character password** (e.g., `abcd efgh ijkl mnop`).
6. In the dashboard top bar, click **"Connect Gmail Account"** → Select **Option 2: Gmail App Password (SMTP)**.
7. Enter your Gmail address, paste your 16-character App Password, and click **Connect via App Password**.
8. **Result**: All job applications sent by the agent will be sent directly through your Gmail account and will appear in your official **Gmail "Sent"** folder!

#### Method B: Google OAuth 2.0 Client ID
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a Project and enable the **Gmail API**.
3. Create an **OAuth 2.0 Client ID** (Application type: *Web application*).
4. Add the Authorized Redirect URI: `http://localhost:8000/api/v1/auth/gmail/callback`.
5. Add `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` to your `backend/.env` file.
6. In the dashboard top bar, click **Connect with Google OAuth**!

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
| **Resumes** | `/api/v1/resumes/upload` | `POST` | Upload PDF resume, extract text, run ATS check & embed in ChromaDB |
| **Resumes** | `/api/v1/resumes/ats-check` | `POST` | Evaluate ATS compatibility score & get recommendations |
| **Search** | `/api/v1/search/trigger` | `POST` | Run RAG & Preferences guided multi-country opportunity search |
| **Search** | `/api/v1/search/opportunities`| `GET` | Fetch aggregated jobs, internships, and scholarships |
| **Matching**| `/api/v1/matching/evaluate` | `POST` | Compute vector RAG semantic match between resume & job |
| **Applications**| `/api/v1/applications` | `GET` / `POST` | List and track active user job applications |
| **Auto Apply**| `/api/v1/auto-apply/send-email`| `POST` | Send CV directly via connected Gmail with message ID tracking |
| **Gmail** | `/api/v1/auth/gmail/status` | `GET` | Get Gmail connection status & connected email |
| **Gmail** | `/api/v1/auth/gmail/setup-smtp` | `POST` | Configure 16-character App Password SMTP credentials |
| **Users** | `/api/v1/users/profile` | `PUT` | Save user profile, social links, target countries, & preferences |

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
- [x] **Phase 2**: PDF parser engine, authentic ATS checker, and vector embeddings in ChromaDB.
- [x] **Phase 3**: RAG & Preferences guided multi-country search aggregator & semantic matching engine.
- [x] **Phase 4**: Interactive Country Autocomplete Search Box (1-10 Countries Max).
- [x] **Phase 5**: Daily Application Goals Tracker & Gmail Auto-Apply email delivery proofs.
- [x] **Phase 6**: Time-based history filters (Today / Monthly / Yearly).
- [ ] **Phase 7**: Chrome / Firefox Extension for one-click job scraping directly from browser tabs.

---

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](file:///c:/Users/Personal/OneDrive/Desktop/Auto-Apply-AI/CONTRIBUTING.md) for details on setting up the project locally, guidelines, and how to find **Good First Issues**.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="center">
  Crafted with ❤️ by <b>Nouman Sajid</b> for <b>Auto Apply AI</b>
</p>
