from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.services.summarizer import SummarizerService

client = TestClient(app)


def test_summarize_messages() -> None:
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": f"summary-{uuid4()}@example.com",
            "password": "StrongPass123",
            "display_name": "Summary Tester",
        },
    )
    headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}

    response = client.post(
        "/v1/ai/summarize",
        headers=headers,
        json={"messages": ["Need the deck by 5", "Client call at 7", "Please send the latest numbers"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]
    assert isinstance(payload["action_items"], list)


def test_summarizer_fallback_returns_summary_and_action_items() -> None:
    summary, action_items = SummarizerService._fallback_summary(
        [
            "Please send the deck before 5 pm",
            "Can you confirm the client call timing?",
            "I will share the latest numbers soon",
        ]
    )

    assert summary
    assert isinstance(action_items, list)
    assert action_items
