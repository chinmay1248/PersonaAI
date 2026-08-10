"""Tests for the context and output cleanup that feed reply quality."""

from app.database import SessionLocal
from app.models.chat_config import ChatConfig
from app.models.chat_message_log import ChatMessageLog
from app.models.user import User
from app.schemas.ai import ConversationMessage, GenerateReplyRequest
from app.services.ai_engine import AIEngineService
from app.services.chat_history_service import ChatHistoryService


def test_merge_history_keeps_the_user_turns_the_client_sent():
    stored = [{"role": "contact", "text": "you coming?"}]
    client = [
        {"role": "contact", "text": "you coming?"},
        {"role": "user", "text": "haan 5 baje"},
        {"role": "contact", "text": "cool"},
    ]

    merged = AIEngineService._merge_history(stored, client)

    assert merged == client
    assert any(message["role"] == "user" for message in merged)


def test_merge_history_prepends_older_stored_messages():
    stored = [
        {"role": "contact", "text": "old one"},
        {"role": "contact", "text": "you coming?"},
    ]
    client = [{"role": "contact", "text": "you coming?"}]

    merged = AIEngineService._merge_history(stored, client)

    assert merged == [
        {"role": "contact", "text": "old one"},
        {"role": "contact", "text": "you coming?"},
    ]


def test_merge_history_falls_back_to_either_side():
    stored = [{"role": "contact", "text": "stored"}]
    assert AIEngineService._merge_history(stored, []) == stored
    assert AIEngineService._merge_history([], stored) == stored


def test_extract_reply_texts_drops_model_preamble_and_formatting():
    raw = (
        "Here are 3 replies you could send:\n"
        "1. \"the black ones? send a pic\"\n"
        "- Reply 2: looks good on you actually\n"
        "* wear that one, easy pick\n"
    )

    replies = AIEngineService._extract_reply_texts(raw, 3)

    assert replies == [
        "the black ones? send a pic",
        "looks good on you actually",
        "wear that one, easy pick",
    ]


def test_extract_reply_texts_drops_trailing_meta_lines():
    raw = "sounds fun, kitne baje?\nchalo phir\nLet me know if you want more options!"

    replies = AIEngineService._extract_reply_texts(raw, 3)

    assert replies == ["sounds fun, kitne baje?", "chalo phir"]


def test_drop_echoed_replies_removes_parroted_message():
    replies = ["kal milna hai kya", "haan bilkul, 5 baje?"]

    assert AIEngineService._drop_echoed_replies(replies, "Kal milna hai kya?") == ["haan bilkul, 5 baje?"]


def test_generate_replies_logs_the_users_own_turn():
    db = SessionLocal()
    try:
        user = User(email="userturn@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()

        chat = ChatConfig(user_id=user.id, chat_label="Test Chat", chat_type="direct")
        db.add(chat)
        db.commit()

        payload = GenerateReplyRequest(
            chat_config_id=chat.id,
            incoming_messages=["so are we on for tomorrow?"],
            conversation_history=[
                ConversationMessage(role="contact", text="hey"),
                ConversationMessage(role="user", text="yeah just got home"),
            ],
            count=2,
        )

        AIEngineService.generate_replies(db, user.id, payload)

        stored = ChatHistoryService.get_chat_history(db, chat.id)
        roles = {message.message_role for message in stored}
        assert roles == {"user", "contact"}
        assert any(message.message_text == "yeah just got home" for message in stored)

        # A second call must not log the same user turn twice.
        AIEngineService.generate_replies(db, user.id, payload)
        user_messages = [
            message for message in ChatHistoryService.get_chat_history(db, chat.id)
            if message.message_role == "user"
        ]
        assert len(user_messages) == 1
    finally:
        db.query(ChatMessageLog).delete()
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()
