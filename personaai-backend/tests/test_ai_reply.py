from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def _auth_header(email: str) -> dict[str, str]:
    register_response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "StrongPass123", "display_name": "AI Tester"},
    )
    token = register_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_generate_reply_flow() -> None:
    headers = _auth_header(f"reply-{uuid4()}@example.com")

    config_response = client.post(
        "/v1/chats/config",
        headers=headers,
        json={
            "chat_label": "Friends Group",
            "chat_type": "friends",
            "personality_mode": "funny",
            "auto_reply_mode": "SMART",
            "ai_enabled": True,
        },
    )
    assert config_response.status_code == 201
    chat_config_id = config_response.json()["id"]

    reply_response = client.post(
        "/v1/ai/generate-reply",
        headers=headers,
        json={
            "chat_config_id": chat_config_id,
            "incoming_messages": ["Hey bro u free tomorrow?"],
            "conversation_history": [{"role": "them", "text": "what's the scene?"}],
            "count": 3,
        },
    )
    assert reply_response.status_code == 200
    payload = reply_response.json()
    assert payload["detected_mood"]
    assert len(payload["suggestions"]) == 3
