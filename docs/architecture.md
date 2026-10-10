# AquaPura — Architecture Overview

> **Status:** Draft — to be updated as the system is built.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Browser                              │
│          React SPA  (Vite + Tailwind CSS)                │
│                                                          │
│  WaterForm  │  ResultCard  │  ExplainChart  │  ChatPanel │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP / REST (JSON)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                          │
│                                                          │
│  /api/predict   /api/assess   /api/history   /api/chat   │
│                                                          │
│       ┌──────────────┐     ┌─────────────────┐          │
│       │  ML Service  │     │  SQLite via ORM  │          │
│       │  (.joblib)   │     │  (SQLAlchemy)    │          │
│       └──────────────┘     └─────────────────┘          │
│                                                          │
│       ┌──────────────────────────────┐                  │
│       │  LLM API (OpenAI / watsonx)  │  ← future        │
│       └──────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

| Component | Responsibility |
|---|---|
| **React SPA** | User interface, form submission, result display, history, chat |
| **FastAPI** | REST API, input validation, model inference, DB access, LLM relay |
| **Scikit-learn Model** | Water potability prediction, feature importance |
| **SQLite** | Optional persistence of assessment history |
| **LLM API** | Conversational answers to water-safety questions |

---

## Data Flow — Prediction Request

1. User fills in the water-quality form and clicks **Assess**.
2. React calls `POST /api/predict` with a JSON body of feature values.
3. FastAPI validates the body with a Pydantic schema.
4. The ML service loads the cached model and runs `model.predict_proba`.
5. SHAP values are computed and sorted by absolute importance.
6. FastAPI returns `{ potable, confidence, feature_importance }`.
7. React renders the verdict card and explanation chart.

---

## Environment Variable Reference

| Variable | Used by | Purpose |
|---|---|---|
| `BACKEND_PORT` | Backend | Uvicorn listen port |
| `CORS_ORIGINS` | Backend | Allowed frontend origins |
| `SECRET_KEY` | Backend | Token signing (future auth) |
| `DATABASE_URL` | Backend | SQLAlchemy connection string |
| `MODEL_PATH` | Backend | Path to `.joblib` model file |
| `LLM_PROVIDER` | Backend | LLM vendor selection |
| `OPENAI_API_KEY` | Backend | OpenAI authentication |
| `WATSONX_API_KEY` | Backend | IBM watsonx.ai authentication |
| `VITE_API_BASE_URL` | Frontend | Backend base URL for fetch calls |

---

## Deployment Targets *(planned)*

- **Local development:** `uvicorn` + `vite dev` separately
- **Docker Compose:** single-command full-stack (`docker compose up`)
- **Cloud:** TBD (Railway / Render / IBM Code Engine)
