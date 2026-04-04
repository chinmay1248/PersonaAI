from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def test_tone_training() -> None:
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": f"tone-{uuid4()}@example.com",
            "password": "StrongPass123",
            "display_name": "Tone Tester",
        },
    )
    headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}

    tone_response = client.post(
        "/v1/tone/train",
        headers=headers,
        json={"samples": ["haha bro this is wild", "yaar chill, sab theek hai"]},
    )
    assert tone_response.status_code == 200
    payload = tone_response.json()
    assert payload["status"] == "trained"
    assert "bro" in payload["slang_patterns"] or "yaar" in payload["slang_patterns"]
