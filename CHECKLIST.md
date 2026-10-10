# AquaPura — Implementation Checklist

Track progress phase by phase. Check off items as they are completed.

---

## Phase 1 · Dataset Preparation

- [x] Identify and download a suitable water-quality dataset — **Kaggle Water Potability**
- [ ] Place raw CSV in `dataset/raw/water_potability.csv` ← **you must do this manually**
- [x] Create EDA script `ml/notebooks/eda.py`
- [x] Create preprocessing script `ml/scripts/preprocess.py`
- [x] Create ML requirements file `ml/requirements_ml.txt`
- [ ] Run `ml/notebooks/eda.py` and review the output in `ml/reports/`
- [ ] Analyse and document missing values, distributions, and class imbalance findings
- [ ] Define and document feature columns and target variable ← partially done in `docs/ml_pipeline.md`
- [ ] Review `ml/scripts/preprocess.py` strategy settings, run it, verify `dataset/processed/water_clean.csv`
- [ ] Document final preprocessing decisions in `docs/ml_pipeline.md`

---

## Phase 2 · Model Training

- [x] Create `ml/scripts/train.py` training script (stub — to be filled in Phase 2)
- [ ] Engineer and select features; document reasoning
- [ ] Split data into train / validation / test sets (stratified)
- [ ] Train baseline model (e.g. Logistic Regression)
- [ ] Train improved model (e.g. Random Forest, Gradient Boosting)
- [ ] Tune hyperparameters (GridSearch / RandomSearch)
- [ ] Evaluate with accuracy, precision, recall, F1, ROC-AUC
- [ ] Save best model artifact to `ml/models/` via `joblib.dump`
- [ ] Save evaluation report to `ml/reports/`

---

## Phase 3 · Prediction API (Backend)

- [ ] Set up FastAPI project structure in `backend/`
- [ ] Create `/api/predict` POST endpoint accepting water-quality features
- [ ] Load and cache model on startup
- [ ] Return prediction label + confidence probability
- [ ] Add Pydantic request / response schemas
- [ ] Implement input validation and error handling
- [ ] Write unit tests for the predict endpoint in `backend/tests/`
- [ ] Document endpoints in `docs/api_reference.md`

---

## Phase 4 · Assessment History (Database)

- [ ] Set up SQLite database with SQLAlchemy
- [ ] Create `Assessment` ORM model (features, prediction, timestamp)
- [ ] `POST /api/assess` — save assessment to DB
- [ ] `GET /api/history` — retrieve paginated history
- [ ] `DELETE /api/history/{id}` — delete a single record
- [ ] Write CRUD unit tests

---

## Phase 5 · Frontend (React + Vite + Tailwind)

- [ ] Initialise Vite project with React template
- [ ] Configure Tailwind CSS
- [ ] Build `WaterForm` component — input fields for each water-quality parameter
- [ ] Build `ResultCard` component — displays potability verdict + confidence
- [ ] Build `HistoryTable` component — past assessments
- [ ] Integrate with backend API via `services/api.js`
- [ ] Add loading states, error boundaries, and form validation
- [ ] Make the UI responsive (mobile-friendly)

---

## Phase 6 · Explainability

- [ ] Add SHAP (or permutation importance) to the backend
- [ ] Return feature importance values alongside prediction
- [ ] Build `ExplainabilityChart` component (horizontal bar chart)
- [ ] Display top contributing factors with plain-language labels
- [ ] Document methodology in `docs/ml_pipeline.md`

---

## Phase 7 · Chatbot Integration

- [ ] Choose LLM provider (OpenAI / IBM watsonx.ai / other)
- [ ] Add API key to `.env` (following `.env.example`)
- [ ] Create `POST /api/chat` endpoint in `backend/app/routers/chat.py`
- [ ] System prompt: water-safety domain expert persona
- [ ] Optionally inject current assessment context into prompt
- [ ] Build `ChatPanel` component in frontend
- [ ] Stream responses if the provider supports it

---

## Phase 8 · Integration & End-to-End Testing

- [ ] Connect all frontend pages to live backend endpoints
- [ ] Write end-to-end tests (Playwright or Cypress)
- [ ] Test full user flow: enter data → predict → view explanation → chat
- [ ] Test edge cases: extreme values, empty fields, API down
- [ ] Cross-browser smoke test (Chrome, Firefox, Safari)

---

## Phase 9 · Deployment

- [ ] Containerise backend with `Dockerfile` (Python / Uvicorn)
- [ ] Containerise frontend with `Dockerfile` (Node build → Nginx)
- [ ] Create `docker-compose.yml` for local full-stack run
- [ ] Choose hosting (Railway, Render, AWS, IBM Code Engine, etc.)
- [ ] Configure CI/CD pipeline (GitHub Actions)
- [ ] Set production environment variables in hosting dashboard
- [ ] Add HTTPS / TLS
- [ ] Write deployment instructions in `docs/architecture.md`

---

## Phase 10 · Documentation & Polish

- [ ] Complete `docs/architecture.md` with final system diagram
- [ ] Complete `docs/api_reference.md` with all endpoints
- [ ] Complete `docs/ml_pipeline.md` with final model details
- [ ] Update `README.md` with live demo link and screenshots
- [ ] Add `CONTRIBUTING.md` and `LICENSE`
- [ ] Accessibility audit (keyboard navigation, ARIA labels)
- [ ] Performance audit (Lighthouse)

---

_Last updated: Phase 1 — EDA scripts and preprocessing pipeline created_
