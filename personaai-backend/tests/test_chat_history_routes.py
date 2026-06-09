from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.chat_tone_profile import ChatToneProfile
from app.services.chat_history_service import ChatHistoryService

client = TestClient(app)


def _register_user() -> tuple[dict[str, str], str]:
    response = client.post(
        "/v1/auth/register",
        json={
            "email": f"history-{uuid4()}@example.com",
            "password": "StrongPass123",
            "display_name": "History Tester",
        },
    )
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}, payload["user_id"]


def _create_chat_config(headers: dict[str, str], label: str = "History Chat") -> str:
    response = client.post(
        "/v1/chats/config",
        headers=headers,
        json={
            "chat_label": label,
            "chat_type": "direct",
            "personality_mode": "funny",
            "auto_reply_mode": "OFF",
            "ai_enabled": True,
            "is_private": False,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_get_chat_history_route_returns_messages_and_total_count() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers)

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="user",
            message_text="hey bro",
            detected_mood="happy",
            language_detected="English",
        )
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="contact",
            message_text="all good?",
            detected_mood="curious",
            language_detected="English",
        )
    finally:
        db.close()

    response = client.get(f"/v1/chats/{chat_config_id}/history", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["chat_id"] == chat_config_id
    assert payload["total_count"] == 2
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["text"] == "all good?"
    assert payload["messages"][0]["role"] == "contact"
    assert payload["messages"][1]["text"] == "hey bro"


def test_get_chat_history_route_supports_mood_filter() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Mood Filter Chat")

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="contact",
            message_text="this is great",
            detected_mood="happy",
        )
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="contact",
            message_text="i am worried",
            detected_mood="concerned",
        )
    finally:
        db.close()

    response = client.get(
        f"/v1/chats/{chat_config_id}/history?mood_filter=happy",
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["mood"] == "happy"
    assert payload["messages"][0]["text"] == "this is great"


