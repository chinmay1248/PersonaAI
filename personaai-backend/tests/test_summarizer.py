from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

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
