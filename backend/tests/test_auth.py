"""
Tests for POST /api/auth/register and POST /api/auth/login.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base, get_db

# ── In-memory SQLite database for tests ────────────────────────────────────
TEST_DATABASE_URL = "sqlite://"   # in-memory, not persisted

test_engine   = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ──────────────────────────────────────────────────────────────────

VALID_USER = {
    "full_name": "Alice Test",
    "email":     "alice@example.com",
    "password":  "securepass123",
}


def register(client, payload=None):
    return client.post("/api/auth/register", json=payload or VALID_USER)


def login(client, email=VALID_USER["email"], password=VALID_USER["password"]):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_register_success(client):
    """POST /api/auth/register returns 201 and the new user object."""
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"]     == VALID_USER["email"]
    assert body["full_name"] == VALID_USER["full_name"]
    assert "id" in body
    # Password must never be returned
    assert "password"        not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    """Registering twice with the same email returns 409."""
    register(client)
    response = register(client)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_register_short_password(client):
    """Password shorter than 8 characters returns 422."""
    payload = {**VALID_USER, "password": "short"}
    response = register(client, payload)
    assert response.status_code == 422


def test_login_valid_credentials(client):
    """POST /api/auth/login with valid credentials returns a JWT."""
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20   # sanity check — not empty


def test_login_wrong_password(client):
    """Login with incorrect password returns 401."""
    register(client)
    response = login(client, password="wrongpassword")
    assert response.status_code == 401


def test_login_unknown_email(client):
    """Login for a non-existent user returns 401."""
    response = login(client, email="nobody@example.com", password="anything")
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    """GET /api/users/me without a token returns 403 (no credentials provided)."""
    response = client.get("/api/users/me")
    # FastAPI HTTPBearer returns 403 when no Authorization header is present
    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client):
    """GET /api/users/me with a bogus token returns 401."""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert response.status_code == 401
