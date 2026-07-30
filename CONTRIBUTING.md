# 🤝 Contributing to Auto Apply AI

Thank you for your interest in contributing to **Auto Apply AI**! We welcome contributions from developers of all skill levels, especially open-source contributors looking for **Good First Issues**.

---

## 📜 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
  - [Finding Good First Issues](#-finding-good-first-issues)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
- [Development Workflow](#-development-workflow)
  - [1. Fork & Clone](#1-fork--clone)
  - [2. Create a Branch](#2-create-a-branch)
  - [3. Make Your Changes](#3-make-your-changes)
  - [4. Test Your Changes](#4-test-your-changes)
  - [5. Submit a Pull Request](#5-submit-a-pull-request)
- [Coding Guidelines](#-coding-guidelines)
  - [Frontend (Next.js & React)](#frontend-nextjs--react)
  - [Backend (FastAPI & Python)](#backend-fastapi--python)
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
- **Python** (v3.12 or higher)
- **Docker & Docker Compose** (for PostgreSQL, Redis, and ChromaDB)
- **Git**

### Local Development Setup

#### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

#### 3. Infrastructure (Optional via Docker)
```bash
docker-compose up -d
```

---

## 🔄 Development Workflow

### 1. Fork & Clone
Fork the repository on GitHub, then clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/Auto-Apply-AI.git
cd Auto-Apply-AI
```

### 2. Create a Branch
Create a descriptive feature or fix branch from `main`:
```bash
git checkout -b feature/add-new-filter
# or
git checkout -b fix/ats-score-bug
```

### 3. Make Your Changes
Write clean, readable, and documented code. Follow the existing project code structure.

### 4. Test Your Changes
- Ensure backend APIs run cleanly without errors (`pytest` if applicable).
- Ensure the frontend builds cleanly without linting/TypeScript errors (`npm run build` or `npm run dev`).

### 5. Submit a Pull Request
1. Commit your changes with a clear commit message:
   ```bash
   git commit -m "feat: add multi-select filter for job roles"
   ```
2. Push to your fork:
   ```bash
   git push origin feature/add-new-filter
   ```
3. Open a Pull Request (PR) against the `main` branch of the official `alfa546/Auto-Apply-AI` repository.
4. Link the PR to any related GitHub Issue (e.g. `Closes #12`).

---

## 📐 Coding Guidelines

### Frontend (Next.js & React)
- Follow modern React patterns (functional components, custom hooks).
- Use TypeScript for strong typing where applicable.
- Style components using CSS modules or Tailwind utility classes following the existing design system.

### Backend (FastAPI & Python)
- Use standard Python typing hints (`Pydantic` schemas).
- Keep endpoint handlers clean and move core business logic into service modules.
- Ensure API endpoints return meaningful HTTP status codes and standard error structures.

---

## 💬 Community & Questions

If you have any questions or need guidance on an issue, feel free to open a discussion or comment directly on the GitHub issue!

Thank you for helping make **Auto Apply AI** better! 🚀
