<p align="center">
  <img src="https://img.shields.io/badge/Auto--Apply--AI-Isolated_AI_Agent_Workspace-FF3B5C?style=for-the-badge&logo=probot&logoColor=white" alt="Auto Apply AI Banner" />
</p>

<h1 align="center">🚀 Auto-Apply AI</h1>

<p align="center">
  <b>An Isolated AI Agent Suite & Automation Workspace for Smart Job Hunting, Resume & ATS Evaluation, Multi-Engine Opportunity Scraping, Playwright Form-Filling, and Direct Gmail Auto-Apply.</b>
</p>

<p align="center">
  <a href="#-key-features"><img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Next.js_16-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Python_3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Tailwind_CSS_v4-FF3B5C?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/SQLite_%2F_PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Redis_7-DC382D?style=flat-square&logo=redis&logoColor=white" alt="Redis"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Ollama_%2F_Local_LLM-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="#-license"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License"></a>
</p>

---

<p align="center">
  <img src="docs/images/login-preview.png" alt="Auto-Apply AI Workspace Preview" width="850" />
</p>

<p align="center">
  <i>🖥️ Auto-Apply AI — Sleek Dark-Grid Workspace Interface with Coral-Red Glow Accents & Real-Time Agent Automation</i>
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
  - [🚀 Single-Command Startup (Recommended)](#-single-command-startup-recommended)
  - [Manual Setup (Alternative)](#manual-setup-alternative)
  - [Connecting Your Gmail Account](#connecting-your-gmail-account)
- [Production Deployment](#-production-deployment)
  - [Docker Compose Deployment](#1-docker-compose-deployment-recommended-for-production)
  - [Linux Systemd & Reverse Proxy Setup](#2-linux-systemd--reverse-proxy-setup)
  - [Platform-as-a-Service (PaaS)](#3-platform-as-a-service-paas)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 Overview

**Auto-Apply AI** is an intelligent, autonomous multi-agent automation platform designed to transform modern job hunting into an efficient, hands-free workflow. Operating as an **isolated AI agent workspace**, it eliminates the tedious friction of manual resume tailoring, scouring fragmented job boards, and drafting repetitive customized cover letters.

Instead of manual repetitive work, **Auto-Apply AI** equips job seekers and engineers with:
1. **Intelligent PDF & Word (`.docx`) Parsing & ATS Grading**: Natively parses complex document structures to extract competencies, experience tiers, and executive summaries while scoring resumes against advanced Applicant Tracking System (ATS) heuristics with actionable structural feedback.
2. **Multi-Engine Opportunity Search & Background Scheduling**: Combines live API integrations (**Adzuna**, **Jooble**), targeted RSS aggregators, and multi-country custom scrapers (e.g., 🇺🇸 US, 🇨🇦 Canada, 🇬🇧 UK, 🇩🇪 Germany, 🇦🇪 UAE) with automated cron-style background refreshers.
3. **LLM Compatibility Matcher & AI Cover Letters**: Evaluates candidate-to-opportunity compatibility in real time using custom prompting strategies, generating highly persuasive, targeted 3-paragraph cover letters tailored specifically to job descriptions.
4. **Playwright Form Filling & Automated Email Extraction**: Autonomously extracts recruiter and hiring manager emails directly from career pages (`email_extractor.py`) and utilizes Playwright browser automation for headless web form submissions (`form_filler.py`).
5. **Multi-Model LLM Vault (Offline & Cloud)**: Full zero-config support for 100% free local offline models (**Ollama / LM Studio**) to ensure data privacy, alongside secure connections to top cloud providers (**OpenAI, Google Gemini, Groq, DeepSeek, OpenRouter**).
6. **Direct Gmail Auto-Apply, Watcher & Reply Classifier**: Authenticates securely via Google OAuth2 or Gmail App Passwords (SMTP) to dispatch custom applications, mirrors proof directly to your Gmail "Sent" folder, watches your inbox for recruiter responses, and intelligently categorizes incoming replies.
7. **Turnkey Launcher & Enterprise Docker DevOps**: Boot instantly on local workstations with a simple `python start.py` command, or scale to production using **Docker Compose** with PostgreSQL 16, Redis 7 caching, and an Nginx reverse proxy.

---

## 🔥 Key Features

### 📄 1. Native PDF & Word (`.docx`) Resume Parsing Engine
- **No-C-Dependency Processing**: Natively parses `.pdf` and `.docx` files with crisp structural fidelity using Python's clean document analyzers (`pdf_parser.py`, `resume_parser.py`).
- **Deep Profile Breakdown**: Autonomously organizes technical skill arrays, employment histories, certifications, and academic credentials.
- **Real-Time ATS Auditor**: Measures formatting density, bullet point impact (action verb frequency), section completeness, and contact visibility (`ats_checker.py`).
- **Resilient Fallback Processing**: Smoothly reverts to heuristic tech-stack keyword extractions if external cloud LLM endpoints hit rate limits.

### 🌐 2. Multi-Engine Job Aggregations & Scheduled Scrapers
- **Live Job APIs & Scraping Hub**: Direct query integrations with **Adzuna** (`adzuna.py`), **Jooble** (`jooble.py`), structured custom job board scrapers (`boards.py`), and RSS feeds (`rss.py`).
- **Multi-Country Targeting**: Select up to 10 destination countries simultaneously via an interactive autocomplete dropdown with customized visual tags (`✓ Country ✕`).
- **Flexible Role Filtering**: Search across full-time careers, internships, academic scholarships, and hackathons with customizable salary thresholds and work arrangements (`Fully Remote`, `Hybrid`, `On-site`).
- **Automated Background Scheduler**: Built-in background aggregation jobs (`scheduler.py`) to keep opportunity pools continuously updated without manual interaction.

### 🤖 3. Playwright Automation & Intelligent Email Extraction
- **Automatic Recruiter Contact Discovery**: Parses opportunity landing pages and job listings to harvest legitimate hiring team email addresses (`email_extractor.py`).
- **Headless Web Form Filling**: Integrates **Playwright** browser automation (`form_filler.py`) to handle repetitive text fields, resume file uploads, and applicant dropdowns on external career portals.
- **Human-In-The-Loop Review**: Optional interactive review modal (`EmailReviewModal.tsx`) allowing candidates to preview, tweak, or approve generated emails and cover letters before dispatch.

### 📧 4. Gmail Auto-Apply, Inbox Watcher & Reply Classifier
- **Dual Authentication Vault**: Establish connections via official **Google OAuth2** or encrypted 16-character **Gmail App Passwords (SMTP)** (`gmail.py`, `gmail_client.py`).
- **Official Sent-Folder Proofs**: Every application dispatched by the AI agent is recorded straight into the candidate's official Gmail "Sent" folder for verifiable transparency.
- **Inbound Reply Watcher**: Regularly inspects inbox responses (`watcher.py`) to identify emails from prospective employers.
- **AI Reply Classification & Drafts**: Automatically categorizes HR responses (e.g., *Interview Invitation*, *Rejection*, *Follow-up Request*) (`classifier.py`) and synthesizes tailored reply drafts (`draft_writer.py`).

### 🔑 5. Universal LLM Vault & Thinking UI
- **Local Offline Privacy**: Natively routes requests to local **Ollama** and **LM Studio** instances (`http://localhost:11434/v1`), keeping confidential career credentials 100% private and free.
- **Cloud Providers Support**: Seamless connectors for OpenAI (`gpt-4o-mini`, `o1`), Google Gemini (`gemini-2.5-flash`), Groq (`llama-3.3-70b-versatile`), DeepSeek, and OpenRouter (`llm_client.py`).
- **Real-Time Agent Feed**: Enjoy a responsive terminal-style streaming UI inside the dashboard that presents real-time AI thought processes, skill evaluations, and matching calculations.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([Candidate / User]) <--> Workspace[Next.js 16 Isolated Workspace Dashboard]
    Workspace <--> REST[FastAPI Asynchronous REST Engine]
    
    subgraph Core Storage, Cache & Database
        REST <--> SQLite[(SQLite / PostgreSQL 16\nSQLAlchemy 2.0 ORM)]
        REST <--> Redis[(Redis 7 Cache\nRate Limiting & Job Queue)]
        REST <--> Storage[Local & Firebase File Storage]
    end

    subgraph Autonomous Multi-Agent Suite
        REST <--> ResumeAgent[Resume & ATS Parsing Agent]
        REST <--> SearchAgent[Multi-Engine Search & Scheduler]
        REST <--> MatchAgent[LLM Matching & Eval Engine]
        REST <--> ApplyAgent[Cover Letter, Gmail & Playwright Agent]
        REST <--> EmailAgent[Inbox Watcher & Reply Classifier]
    end

    subgraph External Models & Integrations
        ResumeAgent & MatchAgent & ApplyAgent & EmailAgent --> LocalLLM[Ollama / LM Studio\n(100% Free Offline LLM)]
        ResumeAgent & MatchAgent & ApplyAgent & EmailAgent --> CloudLLM[OpenAI / Gemini / Groq / DeepSeek]
        ApplyAgent & EmailAgent --> Gmail[Gmail OAuth2 & SMTP Server]
        SearchAgent --> JobAPIs[Adzuna, Jooble, RSS & Custom Scrapers]
        ApplyAgent --> Playwright[Playwright Browser Automation]
    end
```

---

## 🛠️ Tech Stack

| Component | Technology | Highlights & Architectural Role |
| :--- | :--- | :--- |
| **Frontend Dashboard** | Next.js 16 (App Router) | React 19, TypeScript, dynamic UI state, real-time feedback & modular dialogs |
| **Styling & Design System** | Tailwind CSS v4 + Vanilla Tokens | Dark-grid aesthetics, coral-red glow accents, glassmorphism & responsive design |
| **Backend API Engine** | Python 3.12+ / FastAPI | High-performance async request routing with automated OpenAPI/Swagger schematics |
| **Database & ORM** | SQLAlchemy 2.0 (SQLite / PostgreSQL) | Transparent schema introspection, non-destructive syncing & migration readiness |
| **Caching & Job Queues** | Redis 7 + Async Queues | Fast API rate limiting, session management, and asynchronous automation pipelines |
| **Document Processing** | PyPDF2, pdfplumber, python-docx | High-fidelity extraction of headings, tables, bullet points, and plain text |
| **Browser Automation** | Playwright for Python | Autonomous DOM exploration, email scraping, and web portal form submissions |
| **AI & LLM Connectors** | Ollama, OpenAI, Gemini, Groq, DeepSeek | Universal vault architecture supporting automated fallback between providers |
| **Automation Dispatcher** | Gmail API, Async SMTP & OAuth2 | Reliable multi-threaded background email delivery, tracking, and response auditing |

---

## 📁 Repository Structure

```
Auto-Apply-AI/
├── start.py                           # 🚀 Cross-platform single-command full-stack launcher
├── docker-compose.yml                 # 🐳 Multi-service orchestration (Postgres 16, Redis 7, Backend, Frontend, Nginx)
├── nginx.conf                         # 🌐 Production Nginx reverse-proxy & SSL configuration
├── auto-apply-backend.service         # ⚙️ Linux systemd unit for background API execution
├── auto-apply-frontend.service        # ⚙️ Linux systemd unit for workspace UI execution
├── backend/                           # FastAPI Asynchronous Backend Engine
│   ├── src/
│   │   └── app/
│   │       ├── api/                   # REST API Router Endpoints
│   │       │   ├── applications.py    # Application history logs, filters & sent-folder proofs
│   │       │   ├── auth.py            # Workspace user authentication & JWT sessions
│   │       │   ├── auto_apply.py      # Autonomous application runners & batch execution triggers
│   │       │   ├── emails.py          # Cover letter generation, drafts & email dispatching
│   │       │   ├── gmail.py           # Gmail OAuth2 callback & SMTP credentials vault manager
│   │       │   ├── matching.py        # Candidate-to-job AI compatibility & scoring calculator
│   │       │   ├── resumes.py         # Resume document ingestion, profile parsing & ATS audits
│   │       │   ├── search.py          # Multi-engine job aggregations & preferences scanners
│   │       │   └── users.py           # User preference vault, LLM settings & secret masking
│   │       ├── services/              # Core AI, Business Logic & Automation Services
│   │       │   ├── application/       # Cover letter generator, Playwright form filler & pipeline
│   │       │   │   ├── cover_letter.py# Dynamic 3-paragraph AI cover letter synthesizer
│   │       │   │   ├── form_filler.py # Playwright headless web form filler & resume uploader
│   │       │   │   └── pipeline.py    # Multi-stage autonomous job application dispatcher
│   │       │   ├── auto_apply/        # Background execution runner & workflow manager
│   │       │   │   └── runner.py      # Orchestrator for batch job queueing and rate-throttled applies
│   │       │   ├── email/             # Intelligent email suite (Watcher, Classifier & Drafts)
│   │       │   │   ├── classifier.py  # AI classifier for HR responses (Interview, Rejection, Info)
│   │       │   │   ├── draft_writer.py# Autonomous response draft synthesizer for employer emails
│   │       │   │   ├── queue.py       # Async task queue management for outbound dispatches
│   │       │   │   ├── setup_wizard.py# Automated credentials & mailbox connection verifier
│   │       │   │   └── watcher.py     # Inbox monitoring service for tracking recruiter feedback
│   │       │   ├── matching/          # Semantic opportunity-to-resume compatibility engine
│   │       │   │   ├── matcher.py     # LLM evaluation logic & requirement deficit finder
│   │       │   │   └── pipeline.py    # Batch score evaluator for newly discovered jobs
│   │       │   ├── search/            # Job aggregators, APIs & automated web scanners
│   │       │   │   ├── adzuna.py      # Adzuna API integration connector
│   │       │   │   ├── aggregator.py  # Unified job pool normalizer & deduplication engine
│   │       │   │   ├── boards.py      # Custom scrapers for direct career sites and job boards
│   │       │   │   ├── jooble.py      # Jooble API integration connector
│   │       │   │   ├── rss.py         # Specialized RSS academic & hackathon feed reader
│   │       │   │   └── scheduler.py   # Background interval scheduler for automated scans
│   │       │   ├── ats_checker.py     # Real-time ATS formatting, keywords & score audit engine
│   │       │   ├── email_extractor.py # Web scraping utility to find recruiter email contacts
│   │       │   ├── gmail_client.py    # Async Gmail OAuth2 & SMTP client communication wrapper
│   │       │   ├── llm_client.py      # Universal LLM provider bridge (Ollama, OpenAI, Gemini, Groq)
│   │       │   ├── notification.py    # System alerts, execution badges & interactive push reminders
│   │       │   ├── pdf_parser.py      # High-speed PyPDF2 & pdfplumber document reader
│   │       │   └── resume_parser.py   # AI structured extraction for work history & skills arrays
│   │       ├── config.py              # Application environment loader & configuration settings
│   │       ├── database.py            # SQLAlchemy startup engine & schema synchronization
│   │       ├── main.py                # FastAPI lifecycle root, CORS policies & router mounting
│   │       ├── models.py              # Declarative SQL tables (Users, Jobs, Applications, Resumes)
│   │       └── storage.py             # Local filesystem & Firebase file persistent storage
│   ├── requirements.txt               # Backend Python library dependencies
│   └── pyproject.toml                 # Backend formatting and linter configs
├── frontend/                          # Next.js 16 Workspace Dashboard & UI
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/                  # Workspace user sign-in & enrollment routers
│   │   │   ├── components/            # Modular UI Feature Components & Interactive Modals
│   │   │   │   ├── AutoApplyModal.tsx # Setup modal for automated application batches
│   │   │   │   ├── AutoApplyProgress.tsx # Real-time visual application progress monitor
│   │   │   │   ├── EmailReviewModal.tsx  # Human-in-the-loop email & cover letter review window
│   │   │   │   ├── ErrorBoundary.tsx  # Resilience wrapper to capture and recover UI faults
│   │   │   │   ├── GmailModal.tsx     # OAuth2 & SMTP App Password configuration modal
│   │   │   │   ├── HistoryTab.tsx     # Verified sent applications hub (Today, Monthly, Yearly)
│   │   │   │   ├── Icons.tsx          # Customized scalable SVG design icons
│   │   │   │   ├── JobDetailsModal.tsx# Expanded opportunity details, match scores & direct apply
│   │   │   │   ├── JobsTab.tsx        # Multi-country opportunity cards, tag filters & scores
│   │   │   │   ├── Navbar.tsx         # Top branding header & quick-access API Vault launcher
│   │   │   │   ├── ProfileTab.tsx     # Resume drag-and-drop parser & interactive ATS report
│   │   │   │   ├── SettingsTab.tsx    # Multi-model LLM API keys & target job preferences vault
│   │   │   │   ├── Skeletons.tsx      # Smooth skeleton loading shimmers for asynchronous calls
│   │   │   │   └── Toast.tsx          # Micro-animation toast alerts for instant status feedback
│   │   │   ├── context/               # Authentication & workspace configuration React Context
│   │   │   ├── history/               # Application proof tracking page view
│   │   │   ├── opportunities/         # Live job search and filtration page view
│   │   │   ├── profile/               # Candidate qualification & ATS evaluation page view
│   │   │   ├── settings/              # Vault configuration and application parameters page view
│   │   │   ├── layout.tsx             # Root dark-grid layout framework and typography provider
│   │   │   └── page.tsx               # Primary dashboard root navigation controller
│   │   ├── constants.ts               # Globally referenced frontend configs & status tokens
│   │   └── types.ts                   # TypeScript strict interfaces and object data models
│   ├── package.json                   # Frontend dependencies (React 19, Next.js 16, Tailwind v4)
│   └── tailwind.config.ts             # Custom color tokens, glassmorphism templates & animations
├── docs/                              # Documentation assets and interface mockups
├── CONTRIBUTING.md                    # Community contributor guidelines and pull request instructions
├── LICENSE                            # Standard MIT Open-Source License
└── README.md                          # Comprehensive project architecture documentation
```

---

## ⚡ Getting Started

### Prerequisites
- **Python**: v3.10 or higher
- **Node.js**: v18.x or higher
- **Git**: For version control and dependency cloning
- **Redis** & **PostgreSQL** *(Optional — Required only for scale-out production deployments; local development defaults cleanly to lightweight SQLite and internal memory)*.

---

### 🚀 Single-Command Startup (Recommended)

The easiest and fastest way to boot the entire Auto-Apply AI platform on Windows, macOS, or Linux is via our automated cross-platform python launcher:

```bash
python start.py
```

**What `start.py` does autonomously:**
1. ✅ Checks for and installs any missing Python packages (`fastapi`, `uvicorn`, `sqlalchemy`, `playwright`, etc.) via `pip`.
2. ✅ Checks for and installs any missing Node packages (`frontend/node_modules`) via `npm install`.
3. 🚀 Initializes the FastAPI backend REST API server on **`http://localhost:8000`** in the background.
4. 🚀 Initializes the Next.js workspace user interface server on **`http://localhost:3000`** in the background.
5. 🌐 Automatically pops open your system default web browser straight to the **Auto-Apply AI Workspace**.
6. 🛑 Streams live backend & frontend logs in your terminal and shuts down all server processes gracefully when you press `Ctrl + C`.

---

### Manual Setup (Alternative)

If you prefer operating services in isolated interactive terminals for detailed debugging:

#### 1. Backend API Server (Terminal 1)
```bash
cd backend
python -m venv venv

# Activate virtual environment:
# Windows (PowerShell): .\venv\Scripts\Activate.ps1
# Linux / macOS: source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn src.app.main:app --reload --port 8000
```
*API Swagger Documentation will be immediately accessible at `http://localhost:8000/docs`.*

#### 2. Frontend Workspace Dashboard (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
*Workspace Dashboard will be live at `http://localhost:3000`.*

---

### Connecting Your Gmail Account

To authorize the automation agent to dispatch tailored job applications directly from your email:
1. Open your **Auto-Apply AI Workspace** and navigate to **`🔑 API Vault`** (in the top Navbar or inside the **Settings** tab).
2. Under **Connected Gmail Account**, choose between **Google OAuth2** or **Gmail App Password (SMTP)**.
3. For SMTP (Recommended for fast setup): Enter your email address alongside a secure **16-character App Password** (generated via *Google Account > Security > 2-Step Verification > App Passwords*).
4. Click **Connect via App Password**. All cover letters and applications dispatched by the autonomous agents will immediately be verifiable in your official **Gmail "Sent"** folder!

---

## 🐳 Production Deployment

Auto-Apply AI is engineered to run seamlessly on cloud virtual private servers (VPS), enterprise container systems, and managed platforms.

### 1. Docker Compose Deployment (Recommended for Production)
Our unified `docker-compose.yml` config sets up an enterprise production topology complete with **PostgreSQL 16**, **Redis 7** (for background job rate limiting and queuing), **FastAPI Backend**, **Next.js Frontend**, and an **Nginx Reverse Proxy**.

```bash
# Clone the repository and configure your environment variables
cp .env.example .env

# Build and launch all services in detached mode
docker-compose up -d --build
```
- **Backend API**: Accessible via `http://localhost:8000` (or reverse proxied via Nginx on port 80/443).
- **Frontend Workspace**: Accessible via `http://localhost:3000`.
- **Database & Cache**: Automatically linked and persisted using local Docker volumes (`postgres_data`, `redis_data`).

### 2. Linux Systemd & Reverse Proxy Setup
For continuous bare-metal or cloud VPS deployments (Ubuntu / Debian / AlmaLinux):
- **Systemd Unit Files**: Copy `auto-apply-backend.service` and `auto-apply-frontend.service` to `/etc/systemd/system/`.
- **Enable & Start**:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable auto-apply-backend auto-apply-frontend
  sudo systemctl start auto-apply-backend auto-apply-frontend
  ```
- **Nginx Proxying**: Use the provided `nginx.conf` template to route incoming web domain HTTP/HTTPS traffic directly to your local backend and frontend processes.

### 3. Platform-as-a-Service (PaaS)
The repository natively includes a `Procfile`, `runtime.txt` (specifying Python runtime), and `app.json` for rapid zero-config deployments onto platforms such as Heroku, Render, Railway, or Fly.io.

---

## 🔑 Environment Variables

You can configure persistent application behavior by creating a `.env` file in the project root or inside the `backend/` directory (refer to `.env.example`):

```env
# Database & Cache Settings (Defaults to local SQLite auto_apply_local.db if left blank)
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/auto_apply_db"
REDIS_URL="redis://localhost:6379"
POSTGRES_PASSWORD="your_secure_db_password"

# AI Models & Default LLM Providers (Optional: Leave empty when running local Ollama)
OPENAI_API_KEY="your_openai_api_key"
GEMINI_API_KEY="your_gemini_api_key"
LLM_PROVIDER="openai"
LLM_MODEL="gpt-4o-mini"

# Job Aggregator API Keys (Optional for advanced Adzuna / Jooble feeds)
ADZUNA_APP_ID="your_adzuna_app_id"
ADZUNA_APP_KEY="your_adzuna_app_key"
JOOBLE_API_KEY="your_jooble_api_key"

# Gmail OAuth & Storage Configurations (Optional)
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="https://your-domain.com/api/v1/auth/gmail/callback"
FIREBASE_STORAGE_BUCKET="your-firebase-storage-bucket.appspot.com"

# Application Security & Frontend URLs
SECRET_KEY="super-secret-jwt-key-change-in-production"
NEXT_PUBLIC_API_BASE="http://localhost:8000"
CORS_ORIGINS="http://localhost:3000"
```

---

## 📡 API Documentation

Interactive OpenAPI / Swagger documentation is automatically generated whenever the backend server is active at **`http://localhost:8000/docs`**.

| Endpoint | Method | Core Functionality |
| :--- | :---: | :--- |
| `/api/v1/auth/login` | `POST` | Authenticate candidate into their secure workspace session |
| `/api/v1/resumes/upload` | `POST` | Ingest PDF or DOCX file, execute structural parsing & compute ATS rating |
| `/api/v1/resumes/profile` | `GET` / `PUT` | Manage extracted competencies, experience histories & ATS metrics |
| `/api/v1/search/trigger` | `POST` | Invoke multi-engine opportunity aggregators across multi-country feeds |
| `/api/v1/search/opportunities`| `GET` | Retrieve indexed job, internship, scholarship & hackathon listings with filters|
| `/api/v1/matching/evaluate` | `POST` | Perform real-time AI compatibility scoring against opportunity descriptions |
| `/api/v1/auto-apply/run` | `POST` | Trigger autonomous cover letter synthesis and email delivery pipeline |
| `/api/v1/users/settings` | `GET` / `PUT` | Manage encrypted LLM API keys in secure vault & configure career preferences |
| `/api/v1/applications` | `GET` | Retrieve verified transmission logs for Today, Monthly, Yearly or All periods |

---

## 🤝 Contributing

We welcome contributions from developers and researchers! Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guide for instructions on setting up your development environment, coding standards, and bug submission protocols.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full legal text and licensing details.

<p align="center">
  Crafted with ❤️ by <b>Nouman Sajid</b> for <b>Auto-Apply AI</b>
</p>
