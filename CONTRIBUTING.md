# 🤝 Contributing to Auto-Apply AI

Thank you for your interest in contributing to **Auto-Apply AI**! We welcome contributions from developers of all skill levels, especially open-source contributors looking for **Good First Issues**.

---

## 📜 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
  - [Finding Good First Issues](#-finding-good-first-issues)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Single-Command Startup (Recommended)](#-single-command-startup-recommended)
  - [Manual Setup (Alternative)](#-manual-setup-alternative)
- [Project Structure Overview](#-project-structure-overview)
- [Development Workflow](#-development-workflow)
  - [1. Fork & Clone](#1-fork--clone)
  - [2. Create a Branch](#2-create-a-branch)
  - [3. Make Your Changes](#3-make-your-changes)
  - [4. Test Your Changes](#4-test-your-changes)
  - [5. Submit a Pull Request](#5-submit-a-pull-request)
- [Coding Guidelines](#-coding-guidelines)
  - [Frontend (Next.js 16 & React 19)](#frontend-nextjs-16--react-19)
  - [Backend (FastAPI & Python 3.12+)](#backend-fastapi--python-312)
- [Community & Questions](#-community--questions)

---

## 🕊️ Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for everyone. Please treat all contributors with respect, courtesy, and empathy.

---

## 🌟 How Can I Contribute?

There are many ways you can contribute:
- **Reporting Bugs:** Submit issues describing bugs or unexpected behaviors.
- **Suggesting Features:** Propose new ideas or enhancements.
- **Improving Documentation:** Fix typos, clarify guides, or add missing docs.
- **Writing Code:** Fix bugs, add new features, or optimize existing logic.

### 🏷️ Finding Good First Issues

If you are new to the repository or open-source in general:
1. Go to the [Issues](../../issues) tab in GitHub.
2. Filter issues by label: `good first issue` or `help wanted`.
3. Read the issue description, comment that you'd like to work on it, and start coding once assigned!

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed on your machine:
- **Node.js** (v18 or higher) & **npm**
- **Python** (v3.10 or higher; v3.12+ recommended)
- **Git**

> [!NOTE]
> No heavy infrastructure like Docker, Redis, or external vector databases is required for local development! By default, Auto-Apply AI uses a zero-config **SQLite** database and supports free offline LLMs via **Ollama** or **LM Studio**.

### Local Development Setup

#### 🚀 Single-Command Startup (Recommended)
We provide an all-in-one cross-platform launcher that automatically checks dependencies, installs missing packages, starts both frontend and backend servers, and opens the workspace in your browser:

```bash
python start.py
```
- **Frontend Workspace UI:** http://localhost:3000
- **Backend REST API & Docs:** http://localhost:8000/docs

---

#### 🔧 Manual Setup (Alternative)

If you prefer to run services individually across separate terminals:

**1. Backend (FastAPI)**
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn src.app.main:app --reload --port 8000
```

**2. Frontend (Next.js 16)**
```bash
cd frontend
npm install
npm run dev
```

---

## 🏛️ Project Structure Overview

When making contributions, please familiarize yourself with our modular architecture:

- **`start.py`**: Cross-platform launcher script at project root.
- **`backend/src/app/api/`**: FastAPI REST router endpoints (`auth.py`, `resumes.py`, `auto_apply.py`, `applications.py`, etc.).
- **`backend/src/app/services/`**: Core business, parsing, and AI automation logic (`ats_checker.py`, `resume_parser.py`, cover letter generation, opportunity matching, and email dispatchers).
- **`backend/src/app/models.py`**: Declarative SQLAlchemy 2.0 database models.
- **`frontend/src/app/`**: Next.js 16 App Router structure (`/opportunities`, `/history`, `/profile`, `/settings`).
- **`frontend/src/app/components/`**: Reusable modular dashboard components, modals, and design tokens.

---

## 🔄 Development Workflow

### 1. Fork & Clone
Fork the repository on GitHub, then clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/Auto-Apply-AI.git
cd Auto-Apply-AI
```

### 2. Create a Branch
Create a descriptive feature or bugfix branch from `main`:
```bash
git checkout -b feature/add-new-filter
# or
git checkout -b fix/ats-score-calculation
```

### 3. Make Your Changes
Write clean, readable, and documented code. Keep REST API handlers concise by placing core business logic and AI evaluation workflows in service modules.

### 4. Test Your Changes
Before submitting your changes, ensure both frontend and backend verify without errors:

**Backend Verification:**
```bash
cd backend
# Verify SQLAlchemy database model schemas
python src/app/test_db.py
# Run authentication and storage unit tests
python -m unittest src/app/test_auth_storage.py
```

**Frontend Verification:**
```bash
cd frontend
# Ensure TypeScript typing and build pass cleanly
npm run build
```

### 5. Submit a Pull Request
1. Commit your changes with a descriptive commit message:
   ```bash
   git commit -m "feat: enhance resume ATS density parser"
   ```
2. Push to your branch on GitHub:
   ```bash
   git push origin feature/add-new-filter
   ```
3. Open a Pull Request (PR) against the `main` branch of the official repository (`alfa546/Auto-Apply-AI`).
4. Link the PR to any related GitHub Issue (e.g. `Closes #12`).

---

## 📐 Coding Guidelines

### Frontend (Next.js 16 & React 19)
- Follow modern Next.js App Router conventions and component separations.
- Use **TypeScript** for robust typing across components and API data structures (`types.ts`).
- Adhere to the existing **Tailwind CSS v4** design system: maintain our sleek dark-grid aesthetics, coral-red glow accents, and interactive micro-animations.

### Backend (FastAPI & Python 3.12+)
- Use comprehensive Python type hints and explicit **Pydantic** validation schemas.
- Keep REST router handlers in `src/app/api/` clean by delegating core logic, parsing, and LLM communication to service modules in `src/app/services/`.
- Ensure clean SQLite database compatibility and standard SQLAlchemy 2.0 ORM conventions.
- When working on AI/LLM integrations, design features to be compatible with free local models (e.g., Ollama / LM Studio) or use mock providers so other contributors can test offline without paid API keys.

---

## 💬 Community & Questions

If you have any questions or need guidance on an issue, feel free to open a discussion or comment directly on the GitHub issue!

Thank you for helping make **Auto-Apply AI** better! 🚀

