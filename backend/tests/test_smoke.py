"""
Smoke tests -- verify the FastAPI app starts and core endpoints respond.

Run with:
    pytest backend/tests/test_smoke.py -v
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """GET / returns 200 with status=ok."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app"] == "AquaPura"


def test_history_returns_empty_list():
    """GET /api/history returns 200 with an empty items list (Phase 4 stub)."""
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_predict_endpoint_exists():
    """
    POST /api/predict is reachable.  With a valid payload it returns 200
    (model is loaded in the TestClient lifespan).
    This replaces the old 503 stub test -- the model is now wired up.
    """
    payload = {
        "ph": 7.0,
        "hardness": 150.0,
        "solids": 20000.0,
        "chloramines": 7.0,
        "sulfate": 250.0,
        "conductivity": 400.0,
        "organic_carbon": 14.0,
        "trihalomethanes": 66.0,
        "turbidity": 4.0,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
