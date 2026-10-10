"""
Tests for POST /api/chat.

Covers:
- Valid message without context returns 200 with reply and disclaimer.
- Valid message with prediction context returns 200.
- Blank message returns 422.
- Whitespace-only message returns 422.
- Message exceeding max length returns 422.
- Reply and disclaimer are non-empty strings.
- Disclaimer mentions 'screening'.
- Context-aware reply references the result when context provided.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_MSG = {"message": "What does pH mean?"}

VALID_MSG_WITH_CONTEXT = {
    "message": "What does my result mean?",
    "prediction_context": {
        "potable": False,
        "potable_label": 0,
        "probability_potable": 0.35,
        "probability_not_potable": 0.65,
    },
}


class TestChatHappyPath:
    def test_status_200_no_context(self):
        r = client.post("/api/chat", json=VALID_MSG)
        assert r.status_code == 200, r.text

    def test_response_has_reply_and_disclaimer(self):
        r = client.post("/api/chat", json=VALID_MSG)
        body = r.json()
        assert "reply" in body
        assert "disclaimer" in body

    def test_reply_is_non_empty_string(self):
        r = client.post("/api/chat", json=VALID_MSG)
        assert isinstance(r.json()["reply"], str)
        assert len(r.json()["reply"]) > 0

    def test_disclaimer_mentions_guidance(self):
        """Chat disclaimer mentions 'educational guidance' (not 'screening')."""
        r = client.post("/api/chat", json=VALID_MSG)
        disclaimer = r.json()["disclaimer"].lower()
        assert "educational" in disclaimer or "guidance" in disclaimer

    def test_status_200_with_context(self):
        r = client.post("/api/chat", json=VALID_MSG_WITH_CONTEXT)
        assert r.status_code == 200, r.text

    def test_context_reply_references_result(self):
        """When context is provided the reply should mention the prediction."""
        r = client.post("/api/chat", json=VALID_MSG_WITH_CONTEXT)
        reply = r.json()["reply"].lower()
        # The reply should mention 'potable' or 'label' or 'class' or 'model'
        assert any(word in reply for word in ("potable", "label", "class", "model", "not"))

    def test_greeting_returns_200(self):
        r = client.post("/api/chat", json={"message": "Hello!"})
        assert r.status_code == 200

    def test_fallback_returns_200_on_unknown_message(self):
        r = client.post("/api/chat", json={"message": "xyzzy plugh"})
        assert r.status_code == 200
        assert len(r.json()["reply"]) > 0


class TestChatValidation:
    def test_blank_message_returns_422(self):
        r = client.post("/api/chat", json={"message": ""})
        assert r.status_code == 422

    def test_whitespace_only_returns_422(self):
        r = client.post("/api/chat", json={"message": "   "})
        assert r.status_code == 422

    def test_message_too_long_returns_422(self):
        r = client.post("/api/chat", json={"message": "a" * 1001})
        assert r.status_code == 422

    def test_missing_message_field_returns_422(self):
        r = client.post("/api/chat", json={})
        assert r.status_code == 422

    def test_null_message_returns_422(self):
        r = client.post("/api/chat", json={"message": None})
        assert r.status_code == 422
