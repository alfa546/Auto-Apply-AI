<p align="center">
  <img src="https://img.shields.io/badge/Auto--Apply--AI-Isolated_AI_Agent_Workspace-FF3B5C?style=for-the-badge&logo=probot&logoColor=white" alt="Auto Apply AI Banner" />
</p>

<h1 align="center">🚀 Auto-Apply AI</h1>

<p align="center">
  <b>An Autonomous AI Agent Suite & Workspace for Smart Job Hunting, Resume ATS Evaluation, Multi-Engine Scraping, Playwright Form-Filling, and Human-Like Gmail Auto-Apply.</b>
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
- [Anti-Spam & Deliverability (NEW)](#-anti-spam--gmail-deliverability)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Production Deployment](#-production-deployment)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 Overview

**Auto-Apply AI** is an intelligent, autonomous multi-agent automation platform designed to transform modern job hunting into an efficient, hands-free workflow. Operating as an **isolated AI agent workspace**, it eliminates the tedious friction of manual resume tailoring, scouring fragmented job boards, and drafting repetitive customized cover letters.

Instead of manual repetitive work, **Auto-Apply AI** equips job seekers and engineers with:
1. **Intelligent PDF & Word Parsing & ATS Grading**: Natively parses complex document structures and scores resumes against advanced ATS heuristics.
2. **Multi-Engine Opportunity Search**: Combines live API integrations (**Adzuna**, **Jooble**) and multi-country custom scrapers with automated cron-style background refreshers.
3. **LLM Compatibility Matcher & AI Cover Letters**: Evaluates candidate compatibility and generates highly persuasive, targeted cover letters dynamically.
4. **Playwright Form Filling & Automated Email Extraction**: Autonomously extracts recruiter emails directly from career pages and uses Playwright for headless web form submissions.
5. **Universal LLM Vault**: Full support for 100% free local offline models (**Ollama / LM Studio**) alongside secure cloud connections (**OpenAI, Gemini, Groq, DeepSeek**).
6. **Human-Like Gmail Auto-Apply & Inbox Watcher**: Dispatches applications directly from your Gmail account with built-in anti-spam protections (randomized delays, daily limits), mirroring proofs directly to your "Sent" folder.

---

## 🔥 Key Features

### 📄 1. Native Resume Parsing & ATS Engine
- **No-C-Dependency Processing**: Natively parses `.pdf` and `.docx` files with crisp structural fidelity (`pdf_parser.py`, `resume_parser.py`).
- **Deep Profile Breakdown**: Autonomously organizes technical skills, employment histories, certifications, and academic credentials.
- **Real-Time ATS Auditor**: Measures formatting density, action verb frequency, section completeness, and contact visibility (`ats_checker.py`).

### 🌐 2. Multi-Engine Job Aggregations
- **Live Job APIs & Scraping Hub**: Direct query integrations with Adzuna, Jooble, custom job board scrapers, and RSS feeds.
- **Multi-Country Targeting**: Target multiple destinations simultaneously with customizable salary thresholds and work arrangements.
- **Automated Background Scheduler**: Built-in background aggregation jobs keep opportunity pools continuously updated.

### 📧 3. Gmail Auto-Apply & Smart Inbox Watcher
- **Dual Authentication Vault**: Establish connections via Google OAuth2 or encrypted 16-character Gmail App Passwords (SMTP).
- **Official Sent-Folder Proofs**: Every application dispatched is recorded straight into the candidate's official Gmail "Sent" folder.
- **Inbound Reply Watcher**: Regularly inspects inbox responses to identify emails from prospective employers.
- **AI Reply Classification**: Automatically categorizes HR responses (Interview, Rejection, Follow-up) and synthesizes tailored reply drafts.

### 🤖 4. Browser Automation & Form Filling
- **Automatic Recruiter Contact Discovery**: Parses opportunity landing pages to harvest legitimate hiring team email addresses.
- **Headless Web Form Filling**: Integrates **Playwright** browser automation to handle repetitive text fields and resume file uploads on external portals.

### 🔑 5. Universal LLM Vault & Thinking UI
- **Local Offline Privacy**: Natively routes requests to local **Ollama** and **LM Studio** instances, keeping confidential career credentials 100% private.
- **Cloud Providers Support**: Seamless connectors for OpenAI, Google Gemini, Groq, DeepSeek, and OpenRouter.
- **Real-Time Agent Feed**: Enjoy a responsive terminal-style streaming UI inside the dashboard that presents real-time AI thought processes.

---

## 🛡️ Anti-Spam & Gmail Deliverability (New!)

To ensure your Gmail account remains in excellent standing and prevents Google from flagging automated activity, **Auto-Apply AI** includes state-of-the-art deliverability protections:

- **Human-Like Randomized Delays ⏱️**: Instead of blasting emails back-to-back, the background auto-apply runner uses dynamic 8-to-10 minute (`random.randint(480, 600)`) delays between applications. To Google, this perfectly mimics a human typing and sending an email organically.
- **Daily Quota Enforcement 📊**: Built-in daily tracking enforces a maximum number of applications sent per 24 hours (default: 20). Once the limit is reached, the system gracefully halts the runner to protect your account's sender reputation.
- **Dynamic Content Spintax ✍️**: By passing job requirements and your resume profile to the LLM for every single application, no two cover letters are identical. This prevents repetitive content spam-flags.
- **Fallback Email Generation 🏢**: Intelligently sanitizes company domain names to build accurate fallback HR emails (`careers@acmecorp.com`) when direct contacts cannot be scraped.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([Candidate / User]) <--> Workspace[Next.js 16 Isolated Workspace Dashboard]
    Workspace <--> REST[FastAPI Asynchronous REST Engine]
    
    subgraph Core Storage, Cache & Database
        REST <--> SQLite[(SQLite / PostgreSQL 16)]
        REST <--> Redis[(Redis 7 Cache)]
    end

    subgraph Autonomous Multi-Agent Suite
        REST <--> ResumeAgent[Resume & ATS Parsing Agent]
        REST <--> SearchAgent[Multi-Engine Search & Scheduler]
        REST <--> MatchAgent[LLM Matching & Eval Engine]
        REST <--> ApplyAgent[Human-Like Gmail & Playwright Agent]
        REST <--> EmailAgent[Inbox Watcher & Reply Classifier]
    end

    subgraph External Models & Integrations
        ResumeAgent & MatchAgent & ApplyAgent & EmailAgent --> LocalLLM[Ollama / LM Studio]
        ResumeAgent & MatchAgent & ApplyAgent & EmailAgent --> CloudLLM[OpenAI / Gemini / Groq / DeepSeek]
        ApplyAgent & EmailAgent --> Gmail[Gmail OAuth2 & SMTP Server]
        SearchAgent --> JobAPIs[Adzuna, Jooble & Custom Scrapers]
    end
```

---

## 🛠️ Tech Stack

| Component | Technology | Highlights |
| :--- | :--- | :--- |
| **Frontend Dashboard** | Next.js 16 (App Router) | React 19, TypeScript, dynamic UI state, real-time feedback |
| **Styling** | Tailwind CSS v4 | Dark-grid aesthetics, coral-red glow accents, glassmorphism |
| **Backend Engine** | Python 3.12+ / FastAPI | High-performance async request routing & background tasks |
| **Database & ORM** | SQLAlchemy 2.0 | Transparent schema introspection for SQLite / PostgreSQL |
| **Document Processing** | PyPDF2, pdfplumber | High-fidelity extraction of headings, tables, and text |
| **Browser Automation** | Playwright for Python | Autonomous DOM exploration and web portal form submissions |
| **AI & LLM Connectors** | Ollama, OpenAI, Gemini | Universal vault architecture supporting automated fallback |

---

## ⚡ Getting Started

### Prerequisites
- **Python**: v3.10 or higher
- **Node.js**: v18.x or higher
- **Git**: For version control

### 🚀 Single-Command Startup (Recommended)

The easiest and fastest way to boot the entire Auto-Apply AI platform on Windows, macOS, or Linux is via our automated cross-platform python launcher:

```bash
python start.py
```

**What `start.py` does autonomously:**
1. ✅ Installs any missing Python packages via `pip`.
2. ✅ Installs any missing Node packages via `npm install`.
3. 🚀 Initializes the FastAPI backend REST API server on **`http://localhost:8000`**.
4. 🚀 Initializes the Next.js workspace user interface server on **`http://localhost:3000`**.
5. 🌐 Automatically opens your web browser to the Workspace.

---

## 🐳 Production Deployment

### Docker Compose Deployment
Our unified `docker-compose.yml` config sets up an enterprise production topology complete with **PostgreSQL 16**, **Redis 7**, **FastAPI**, **Next.js**, and **Nginx**.

```bash
cp .env.example .env
docker-compose up -d --build
```
- **Backend API**: `http://localhost:8000`
- **Frontend Workspace**: `http://localhost:3000`

---

## 🔑 Environment Variables

You can configure persistent application behavior by creating a `.env` file in the project root:

```env
# Database Settings (Defaults to local SQLite auto_apply_local.db if left blank)
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/auto_apply_db"

# AI Models
OPENAI_API_KEY="your_openai_api_key"
GEMINI_API_KEY="your_gemini_api_key"

# Gmail OAuth Configurations
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/gmail/callback"

# Application Security
SECRET_KEY="super-secret-jwt-key-change-in-production"
```

---

## 📡 API Documentation

Interactive OpenAPI / Swagger documentation is automatically generated whenever the backend server is active at **`http://localhost:8000/docs`**.

| Endpoint | Method | Core Functionality |
| :--- | :---: | :--- |
| `/api/v1/auth/login` | `POST` | Authenticate candidate into their secure workspace |
| `/api/v1/resumes/upload` | `POST` | Ingest PDF, execute structural parsing & compute ATS rating |
| `/api/v1/search/trigger` | `POST` | Invoke multi-engine opportunity aggregators |
| `/api/v1/matching/evaluate` | `POST` | Perform real-time AI compatibility scoring |
| `/api/v1/auto-apply/run` | `POST` | Trigger autonomous background email delivery pipeline |

---

## 🤝 Contributing

We welcome contributions from developers and researchers! Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guide for instructions on setting up your development environment.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full legal text and licensing details.

<p align="center">
  Crafted with ❤️ by <b>Nouman Sajid</b> for <b>Auto-Apply AI</b>
</p>
