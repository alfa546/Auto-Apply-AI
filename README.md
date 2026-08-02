<p align="center">
  <img src="https://img.shields.io/badge/Auto--Apply--AI-Isolated_AI_Agent_Workspace-FF3B5C?style=for-the-badge&logo=probot&logoColor=white" alt="Auto Apply AI Banner" />
</p>

<h1 align="center">🚀 Auto-Apply AI</h1>

<p align="center">
  <b>An Isolated AI Agent Suite & Automation Workspace for Smart Job Hunting, Resume & ATS Evaluation, Preferences-Guided Multi-Country Scraping, and Direct Gmail Auto-Apply.</b>
</p>

<p align="center">
  <a href="#-key-features"><img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Next.js_16-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Python_3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/Tailwind_CSS_v4-FF3B5C?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind"></a>
  <a href="#-key-features"><img src="https://img.shields.io/badge/SQLite_%2F_PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
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
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [License](#-license)

---

## 💡 Overview

**Auto-Apply AI** is an intelligent, autonomous multi-agent automation platform designed to transform modern job hunting into an efficient, hands-free workflow. Operating as an **isolated AI agent workspace**, it takes over the tedious tasks of editing resumes, searching across multiple job portals, and writing repetitive customized emails.

Instead of manual applications, **Auto-Apply AI** empowers candidates with:
1. **Intelligent PDF & Word (`.docx`) Parsing & ATS Grading**: Natively extracts competencies, work histories, and executive summaries, scoring resumes against modern Applicant Tracking System (ATS) guidelines with interactive formatting feedback.
2. **Preferences-Guided Opportunity Search**: Synthesizes your specific target roles, experience levels, remote preferences, and resume skills to execute hyper-targeted scans across up to 10 destination countries simultaneously (e.g., 🇺🇸 US, 🇨🇦 Canada, 🇬🇧 UK, 🇩🇪 Germany, 🇦🇪 UAE).
3. **LLM Matching Engine & AI Cover Letters**: Dynamically evaluates opportunity compatibility using customized AI prompting, generating highly persuasive, tailored 3-paragraph cover letters for matching positions.
4. **Multi-Model LLM Vault (Offline & Cloud)**: Fully compatible with 100% free local offline models (Ollama / LM Studio), alongside secure integration with leading cloud providers (OpenAI, Google Gemini, Groq, DeepSeek, and OpenRouter).
5. **Direct Gmail Auto-Apply & Proofs Hub**: Authenticates securely via Google OAuth2 or Gmail App Passwords (SMTP) to dispatch custom applications directly to hiring managers, logging verifiable message proofs straight in your Gmail "Sent" folder.
6. **One-Command Launcher**: Effortlessly initialize both backend servers, frontend dashboards, and dependencies with a simple `python start.py` command.

---

## 🔥 Key Features

### 📄 1. Native PDF & Word (`.docx`) Resume Parsing Engine
- **No-C-Dependency Processing**: Natively parses both `.pdf` and Word `.docx` documents using Python's clean structural extractors.
- **Deep Profile Breakdown**: Automatically extracts executive summaries, technical skill arrays, employment experience tiers, and academic credentials.
- **Real-Time ATS Auditor**: Evaluates formatting density, bullet point action verbs (e.g., *Orchestrated*, *Optimized*), section structure, and contact information availability.
- **Resilient Fallback Parsing**: Seamlessly falls back to heuristic tech-stack extraction if an external LLM key is offline or out of quota.

### 🧠 2. Real-Time LLM Agent Workspace & Thinking UI
- **Live Agent Feed**: Experience a responsive terminal-style log feed inside your dashboard that outputs real-time AI reasoning, skill extractions, and matcher evaluations.
- **Dark Grid & Coral-Red Aesthetic**: Designed with state-of-the-art glassmorphic overlays, harmonious dark color palettes, and interactive micro-animations.

### 🌐 3. Preferences-Guided Multi-Country Job & Internship Aggregator
- **Target Country Multi-Selection**: Select up to 10 target countries simultaneously via an interactive autocomplete dropdown with custom tag badges (`✓ Country ✕`).
- **Flexible Opportunity Filters**: Search not only full-time roles, but also internships, scholarships, and hackathons with customizable salary bands and remote filters (`Fully Remote`, `Hybrid`, `On-site`).

### 🔑 4. Universal LLM Providers Vault
- **Free Local LLMs**: Built-in, zero-config support for local **Ollama** and **LM Studio** endpoints (`http://localhost:11434/v1`), keeping your private career data 100% offline and free.
- **Cloud Providers Support**: Connect seamlessly to OpenAI (`gpt-4o-mini`), Groq (`llama-3.3-70b-versatile`), Google Gemini (`gemini-2.5-flash`), DeepSeek, and OpenRouter.
- **Secure Secret Masking**: All keys stored within the isolated workspace vault are encrypted and visually masked in the UI.

### 📧 5. Direct Gmail Auto-Apply & Proof Tracking
- **Dual Authentication**: Establish connections either through Google OAuth2 or an encrypted 16-character Gmail App Password (SMTP).
- **History & Proofs Hub**: Track all delivered applications with time-period filtering (**Today / 24 Hours**, **Monthly**, **Yearly**, or **All Time**).
- **Official Sent-Folder Logs**: Every application email dispatched by the automation agent gets recorded directly in the candidate’s official Gmail "Sent" folder for transparent verification.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([Candidate / User]) <--> Workspace[Next.js 16 Isolated Workspace Dashboard]
    Workspace <--> REST[FastAPI Asynchronous REST Engine]
    
    subgraph Core Storage & Database
        REST <--> SQLite[(SQLite / PostgreSQL\nSQLAlchemy 2.0 ORM)]
        REST <--> Storage[Local & Firebase File Storage]
    end

    subgraph Autonomous Multi-Agent Suite
        REST <--> ResumeAgent[Resume & ATS Parsing Agent]
        REST <--> SearchAgent[Preferences-Guided Search Agent]
        REST <--> MatchAgent[LLM Matching & Eval Engine]
        REST <--> ApplyAgent[Cover Letter & Auto-Apply Agent]
    end

    subgraph External Models & Integrations
        ResumeAgent & MatchAgent & ApplyAgent --> LocalLLM[Ollama / LM Studio\n(100% Free Offline LLM)]
        ResumeAgent & MatchAgent & ApplyAgent --> CloudLLM[OpenAI / Gemini / Groq / DeepSeek]
        ApplyAgent --> Gmail[Gmail OAuth2 & SMTP Server]
        SearchAgent --> JobAPIs[Multi-Country Job Feed Scrapers & RSS]
    end
```

---

## 🛠️ Tech Stack

| Component | Technology | Highlights & Details |
| :--- | :--- | :--- |
| **Frontend Platform** | Next.js 16 (App Router) | React 19, TypeScript, dynamic UI state & interactive modals |
| **UI Design System** | Tailwind CSS v4 + Vanilla Tokens | Dark-grid aesthetics, coral-red glow effects, modern responsive layouts |
| **Backend Engine** | Python 3.12+ / FastAPI | Asynchronous performance, automatic Swagger/OpenAPI documentation |
| **Database & ORM** | SQLAlchemy 2.0 (SQLite / PostgreSQL) | Automatic table introspection & non-destructive schema synchronization |
| **Document Processing**| PyPDF2, pdfplumber, python-docx | High-fidelity structural parsing for PDF and Word formats |
| **AI & LLM Engine** | Ollama, OpenAI, Google GenAI, Groq | Multi-provider architecture with fallback capabilities |
| **Automation Dispatcher** | Gmail API & Async SMTP | Reliable background job delivery and verification tracking |

---

## 📁 Repository Structure

```
Auto-Apply-AI/
├── start.py                        # 🚀 Single-command cross-platform full-stack launcher
├── backend/                        # FastAPI Backend Engine
│   ├── src/
│   │   └── app/
│   │       ├── api/                # REST API Endpoints
│   │       │   ├── applications.py # Application proof logs & verification
│   │       │   ├── auth.py         # Workspace user authentication
│   │       │   ├── auto_apply.py   # Autonomous job application triggers
│   │       │   ├── emails.py       # Cover letter generation & email sending
│   │       │   ├── gmail.py        # Gmail OAuth & SMTP credentials manager
│   │       │   ├── matching.py     # LLM evaluation & job score calculations
│   │       │   ├── resumes.py      # Resume uploading, parsing & ATS audit
│   │       │   ├── search.py       # Preferences-guided opportunity scanners
│   │       │   └── users.py        # User settings & API Vault manager
│   │       ├── services/           # Core AI & Business Services
│   │       │   ├── application/    # Intelligent AI Cover letter creator
│   │       │   ├── matching/       # Opportunity-to-resume evaluation engine
│   │       │   ├── search/         # Aggregators & preferences-guided agents
│   │       │   ├── ats_checker.py  # ATS criteria rating & formatting tips
│   │       │   └── pdf_parser.py   # Native document text extractor
│   │       ├── config.py           # Application config & environment loader
│   │       ├── database.py         # Engine startup & auto-sync schema setup
│   │       ├── main.py             # Server initialization & CORS policies
│   │       ├── models.py           # Declarative SQL database models
│   │       └── storage.py          # Local filesystem & Firebase file storage
│   ├── requirements.txt            # Backend Python dependencies
│   └── pyproject.toml              # Backend environment configs
├── frontend/                       # Next.js 16 Workspace Dashboard
│   ├── src/
│   │   └── app/
│   │       ├── components/         # Modular Dashboard Components & Tabs
│   │       │   ├── GmailModal.tsx  # Gmail authentication & SMTP modal
│   │       │   ├── HistoryTab.tsx  # Today / Monthly / Yearly application hub
│   │       │   ├── JobsTab.tsx     # Opportunity cards, score badges & filters
│   │       │   ├── Navbar.tsx      # Top branding bar & quick-access vault
│   │       │   ├── ProfileTab.tsx  # Resume parser upload & ATS report UI
│   │       │   └── SettingsTab.tsx # Multi-LLM provider & Preferences Vault
│   │       ├── context/            # Client Authentication & State Context
│   │       ├── layout.tsx          # Root styling and theme framework
│   │       └── page.tsx            # Main application navigation router
│   ├── package.json                # Node modules and build scripts
│   └── tailwind.config.ts          # UI styling & design tokens
├── docs/                           # Documentation & Preview Media
│   └── images/
│       └── login-preview.png       # Dark grid login workspace UI graphic
├── LICENSE                         # Standard MIT Open-Source License
└── README.md                       # Comprehensive repository documentation
```

---

## ⚡ Getting Started

### Prerequisites
- **Python**: v3.10 or higher
- **Node.js**: v18.x or higher
- **Git**

---

### 🚀 Single-Command Startup (Recommended)

The easiest way to boot the entire Auto-Apply AI platform on Windows, macOS, or Linux is using our cross-platform automation launcher:

```bash
python start.py
```

**What `start.py` does automatically:**
1. ✅ Verifies and Installs missing Python packages (`fastapi`, `uvicorn`, `sqlalchemy`, etc.) via `pip`.
2. ✅ Verifies and Installs missing Node packages (`frontend/node_modules`) via `npm install`.
3. 🚀 Launches the FastAPI backend API server on **`http://localhost:8000`** in the background.
4. 🚀 Launches the Next.js workspace UI server on **`http://localhost:3000`** in the background.
5. 🌐 Automatically opens your default web browser straight to the **Auto-Apply AI Workspace**.
6. 🛑 Streams real-time terminal logs and closes all server processes gracefully when you press `Ctrl + C`.

---

### Manual Setup (Alternative)

If you prefer launching services independently across two terminals:

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
*API Documentation will be accessible at `http://localhost:8000/docs`.*

#### 2. Frontend Workspace Dashboard (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
*Workspace UI will be accessible at `http://localhost:3000`.*

---

### Connecting Your Gmail Account

To authorize the automation agent to dispatch customized applications directly from your email:
1. Log into your **Auto-Apply AI Workspace** and navigate to **`🔑 API Vault`** (or the **Settings** tab).
2. Under **Connected Gmail Account**, choose **Gmail App Password (SMTP)**.
3. Input your email address along with a secure **16-character App Password** (easily generated via *Google Account > Security > 2-Step Verification > App Passwords*).
4. Click **Connect via App Password**. All automated emails and cover letters dispatched by the AI will immediately be mirrored and verifiable in your official **Gmail "Sent"** folder!

---

## 🔑 Environment Variables

You can optionally configure default behaviors by creating a `.env` file inside the `backend/` directory:

```env
# Database Settings (Defaults to local SQLite auto_apply_local.db if left blank)
DATABASE_URL="sqlite:///./auto_apply_local.db"

# AI Models & Default LLM Providers (Optional: Leave empty when using local Ollama)
OPENAI_API_KEY="your_openai_api_key"
LLM_PROVIDER="openai"
LLM_MODEL="gpt-4o-mini"

# Gmail OAuth & Storage Configurations (Optional)
GMAIL_CLIENT_ID="your_google_client_id"
GMAIL_CLIENT_SECRET="your_google_client_secret"
FIREBASE_STORAGE_BUCKET="your-firebase-storage-bucket.appspot.com"

# Application Security
SECRET_KEY="super-secret-jwt-key-change-in-production"
```

---

## 📡 API Documentation

Interactive OpenAPI/Swagger documentation is automatically published whenever the backend server runs at `http://localhost:8000/docs`.

| Endpoint | Method | Core Functionality |
| :--- | :---: | :--- |
| `/api/v1/auth/login` | `POST` | Authenticate candidate into their isolated workspace |
| `/api/v1/resumes/upload` | `POST` | Ingest PDF/DOCX resume file, extract structural data & compute ATS score |
| `/api/v1/resumes/profile` | `GET` / `PUT` | Manage extracted candidate qualifications, skills array & ATS metrics |
| `/api/v1/search/trigger` | `POST` | Invoke the **Preferences-Guided Search Agent** across multi-country feeds |
| `/api/v1/search/opportunities`| `GET` | Retrieve scraped job, internship & scholarship listings with filters |
| `/api/v1/matching/evaluate` | `POST` | Perform real-time AI evaluation and compatibility scoring against job postings |
| `/api/v1/auto-apply/run` | `POST` | Trigger autonomous cover letter synthesis and Gmail delivery pipeline |
| `/api/v1/users/settings` | `GET` / `PUT` | Store LLM API keys in secure vault & customize remote job preferences |
| `/api/v1/applications` | `GET` | Access verified transmission logs for Today, Monthly, Yearly or All periods |

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](file:///c:/Users/Personal/OneDrive/Desktop/Auto-Apply-AI/LICENSE) for full legal text and details.

<p align="center">
  Crafted with ❤️ by <b>Nouman Sajid</b> for <b>Auto-Apply AI</b>
</p>
