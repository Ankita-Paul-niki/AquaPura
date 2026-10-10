# 💧 AquaPura

**AI-powered water-quality assessment and potability prediction web application.**

AquaPura lets users submit water-quality measurements and receive an instant
potability prediction, an explainability breakdown of the key contributing
factors, and an optional AI-powered chatbot that answers follow-up questions
about water safety.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Roadmap](#roadmap)

---

## Overview

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend API | Python 3.11+, FastAPI, Uvicorn |
| Machine Learning | Pandas, NumPy, Scikit-learn |
| Database | SQLite (via SQLAlchemy) |
| Chatbot *(planned)* | LLM API (e.g. OpenAI / watsonx) |

---

## Architecture

```
Browser (React SPA)
       │  REST / JSON
       ▼
FastAPI Backend  ──►  SQLite DB (assessment history)
       │
       ▼
Scikit-learn Model (.joblib)
       │
       ▼
SHAP / Feature Importance  ──►  Explainability response
```

The frontend is a standalone Vite app that communicates with the FastAPI backend
over a REST API. The ML model is loaded once at startup and reused for every
prediction request. Assessment results are optionally persisted in a local SQLite
database for history and analytics.

---

## Folder Structure

```
AquaPura/
├── frontend/          # React + Vite + Tailwind SPA
├── backend/           # FastAPI REST API
├── ml/                # Training scripts, notebooks, saved models
├── dataset/           # Raw and processed data files
├── docs/              # Architecture, API, and ML documentation
├── README.md
├── .gitignore
├── .env.example
└── CHECKLIST.md
```

---

## Prerequisites

Make sure you have the following installed before running AquaPura locally:

- **Node.js** ≥ 18 and **npm** ≥ 9  →  [nodejs.org](https://nodejs.org)
- **Python** ≥ 3.11  →  [python.org](https://python.org)
- **Git**  →  [git-scm.com](https://git-scm.com)

---

## Quick Start

### 1 · Clone the repository

```bash
git clone https://github.com/your-org/aquapura.git
cd aquapura
```

### 2 · Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in your real values
```

### 3 · Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

### 4 · Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.  
See [docs/architecture.md](docs/architecture.md) for a full description of each key.

---

## Roadmap

See [CHECKLIST.md](CHECKLIST.md) for the detailed phase-by-phase implementation plan.

---

> AquaPura is under active development. APIs and data schemas may change.
