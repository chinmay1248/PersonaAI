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


def test_get_recent_messages_route_returns_only_recent_entries() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Recent Chat")

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="user",
            message_text="fresh message",
            detected_mood="happy",
        )
    finally:
        db.close()

    response = client.get(f"/v1/chats/{chat_config_id}/history/recent?minutes=5", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_count"] == 1
    assert payload["messages"][0]["text"] == "fresh message"


def test_get_chat_tone_profile_route_returns_profile() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Tone Profile Chat")

    db = SessionLocal()
    try:
        tone_profile = ChatToneProfile(
            chat_config_id=chat_config_id,
            user_id=user_id,
            avg_message_length=8.5,
            emoji_frequency=0.2,
            common_emojis=["😊"],
            slang_patterns=["bro", "lol"],
            punctuation_style="expressive",
            formality_score=2.1,
            caps_usage="lowercase",
            language_mix=["English"],
            tone_shifts={},
            message_openers=["hey"],
            message_closers=["lol"],
            response_timing={},
        )
        db.add(tone_profile)
        db.commit()
    finally:
        db.close()

    response = client.get(f"/v1/chats/{chat_config_id}/tone-profile", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["chat_config_id"] == chat_config_id
    assert payload["punctuation_style"] == "expressive"
    assert payload["slang_patterns"] == ["bro", "lol"]
    assert payload["message_openers"] == ["hey"]


def test_get_chat_tone_profile_route_returns_404_when_missing() -> None:
    headers, _user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Missing Tone Chat")

    response = client.get(f"/v1/chats/{chat_config_id}/tone-profile", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Tone profile not trained yet"


def test_retrain_chat_tone_route_creates_profile_from_user_messages() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Retrain Tone Chat")

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="user",
            message_text="hey bro this is wild lol!",
        )
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="user",
            message_text="yeah i got you bro 😊",
        )
    finally:
        db.close()

    response = client.post(f"/v1/chats/{chat_config_id}/retrain-tone", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "trained"
    assert payload["chat_config_id"] == chat_config_id
    assert payload["avg_message_length"] > 0

    verify_db = SessionLocal()
    try:
        stored_profile = verify_db.query(ChatToneProfile).filter(
            ChatToneProfile.chat_config_id == chat_config_id
        ).one_or_none()
        assert stored_profile is not None
        assert "bro" in (stored_profile.slang_patterns or [])
    finally:
        verify_db.close()


def test_export_chat_history_route_respects_include_encrypted_flag() -> None:
    headers, user_id = _register_user()
    chat_config_id = _create_chat_config(headers, label="Export Chat")

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role="contact",
            message_text="keep this visible",
            detected_mood="neutral",
        )
    finally:
        db.close()

    default_response = client.get(f"/v1/chats/{chat_config_id}/export", headers=headers)
    decrypted_response = client.get(
        f"/v1/chats/{chat_config_id}/export?include_encrypted=true",
        headers=headers,
    )

    assert default_response.status_code == 200
    assert default_response.json()["messages"][0]["text"] == "[encrypted]"
    assert decrypted_response.status_code == 200
    assert decrypted_response.json()["messages"][0]["text"] == "keep this visible"


def test_chat_history_routes_enforce_chat_ownership() -> None:
    owner_headers, owner_user_id = _register_user()
    intruder_headers, _intruder_user_id = _register_user()
    chat_config_id = _create_chat_config(owner_headers, label="Private Chat")

    db = SessionLocal()
    try:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat_config_id,
            user_id=owner_user_id,
            message_role="contact",
            message_text="secret message",
        )
    finally:
        db.close()

    response = client.get(f"/v1/chats/{chat_config_id}/history", headers=intruder_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"
