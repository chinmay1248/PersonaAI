"""
Tests for ChatHistoryService - per-chat message logging and retrieval.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.database import SessionLocal
from app.models.user import User
from app.models.chat_config import ChatConfig
from app.models.chat_message_log import ChatMessageLog
from app.services.chat_history_service import ChatHistoryService


@pytest.fixture
def setup_test_data():
    """Create test user and chat configuration."""
    db = SessionLocal()
    user = User(email="test@example.com", password_hash="hashed", display_name="Test User")
    db.add(user)
    db.flush()

    chat = ChatConfig(
        user_id=user.id,
        chat_label="Test Chat",
        chat_type="direct"
    )
    db.add(chat)
    db.commit()

    yield db, user, chat

    # Cleanup
    db.query(ChatMessageLog).delete()
    db.query(ChatConfig).delete()
    db.query(User).delete()
    db.commit()
    db.close()


def test_log_message(setup_test_data):
    """Test logging a single message."""
    db, user, chat = setup_test_data

    message = ChatHistoryService.log_message(
        db=db,
        chat_config_id=chat.id,
        user_id=user.id,
        message_role="user",
        message_text="Hey, how are you?",
        detected_mood="friendly",
        language_detected="en"
    )

    assert message.id is not None
    assert message.message_role == "user"
    assert message.message_text == "Hey, how are you?"
    assert message.detected_mood == "friendly"
    assert message.language_detected == "en"


def test_get_chat_history(setup_test_data):
    """Test retrieving chat history."""
    db, user, chat = setup_test_data

    # Log multiple messages
    messages_data = [
        ("user", "Hello!", "happy", "en"),
        ("contact", "Hi there!", "happy", "en"),
        ("user", "How are you?", "curious", "en"),
        ("contact", "I'm good, thanks!", "happy", "en"),
    ]

    for role, text, mood, lang in messages_data:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
            detected_mood=mood,
            language_detected=lang
        )

    # Retrieve history
    history = ChatHistoryService.get_chat_history(db, chat.id, limit=10)

    assert len(history) == 4
    # History is returned in reverse chronological order
    assert history[0].message_text == "I'm good, thanks!"
    assert history[-1].message_text == "Hello!"


def test_get_user_messages_only(setup_test_data):
    """Test retrieving only user's own messages."""
    db, user, chat = setup_test_data

    messages_data = [
        ("user", "Message 1"),
        ("contact", "Response 1"),
        ("user", "Message 2"),
        ("contact", "Response 2"),
    ]

    for role, text in messages_data:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
        )

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=10)

    assert len(user_messages) == 2
    assert all(msg.message_role == "user" for msg in user_messages)
    assert "Message 1" in [msg.message_text for msg in user_messages]
    assert "Message 2" in [msg.message_text for msg in user_messages]


def test_get_contact_messages_only(setup_test_data):
    """Test retrieving only incoming messages."""
    db, user, chat = setup_test_data

    messages_data = [
        ("user", "Message 1"),
        ("contact", "Response 1"),
        ("user", "Message 2"),
        ("contact", "Response 2"),
    ]

    for role, text in messages_data:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
        )

    contact_messages = ChatHistoryService.get_contact_messages_only(db, chat.id, limit=10)

    assert len(contact_messages) == 2
    assert all(msg.message_role == "contact" for msg in contact_messages)
    assert "Response 1" in [msg.message_text for msg in contact_messages]
    assert "Response 2" in [msg.message_text for msg in contact_messages]


def test_get_recent_messages(setup_test_data):
    """Test retrieving messages from a specific time window."""
    db, user, chat = setup_test_data

    # Log old message
    old_message = ChatMessageLog(
        chat_config_id=chat.id,
        user_id=user.id,
        message_role="user",
        message_text="Old message",
        created_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    db.add(old_message)
    db.flush()

    # Log recent message
    ChatHistoryService.log_message(
        db=db,
        chat_config_id=chat.id,
        user_id=user.id,
        message_role="user",
        message_text="Recent message",
    )

    # Get messages from last 24 hours
    recent = ChatHistoryService.get_recent_messages(db, chat.id, minutes=1440)

    assert len(recent) == 1
    assert recent[0].message_text == "Recent message"


def test_search_messages_by_mood(setup_test_data):
    """Test searching messages by detected mood."""
    db, user, chat = setup_test_data

    messages_data = [
        ("user", "Great!", "happy"),
        ("contact", "Awesome!", "happy"),
        ("user", "I'm worried", "concerned"),
        ("contact", "Don't worry", "concerned"),
    ]

    for role, text, mood in messages_data:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
            detected_mood=mood,
        )

    happy_messages = ChatHistoryService.search_messages_by_mood(db, chat.id, "happy", limit=10)
    concerned_messages = ChatHistoryService.search_messages_by_mood(db, chat.id, "concerned", limit=10)

    assert len(happy_messages) == 2
    assert len(concerned_messages) == 2
    assert all(msg.detected_mood == "happy" for msg in happy_messages)
    assert all(msg.detected_mood == "concerned" for msg in concerned_messages)


def test_get_message_count(setup_test_data):
    """Test getting total message count."""
    db, user, chat = setup_test_data

    for i in range(5):
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role="user" if i % 2 == 0 else "contact",
            message_text=f"Message {i}",
        )

    count = ChatHistoryService.get_message_count(db, chat.id)
    assert count == 5


def test_export_chat_history(setup_test_data):
    """Test exporting full chat history."""
    db, user, chat = setup_test_data

    ChatHistoryService.log_message(
        db=db,
        chat_config_id=chat.id,
        user_id=user.id,
        message_role="user",
        message_text="Test message",
        detected_mood="happy",
    )

    export_data = ChatHistoryService.export_chat_history(db, chat.id)

    assert export_data["chat_label"] == "Test Chat"
    assert export_data["total_messages"] == 1
    assert len(export_data["messages"]) == 1
    assert export_data["messages"][0]["text"] == "[encrypted]"  # Encryption by default

    # Export with decryption
    export_data_decrypted = ChatHistoryService.export_chat_history(db, chat.id, include_encrypted=True)
    assert export_data_decrypted["messages"][0]["text"] == "Test message"


def test_format_for_prompt(setup_test_data):
    """Test formatting chat history for inclusion in prompt."""
    db, user, chat = setup_test_data

    logs = []
    for role, text in [("user", "Hello"), ("contact", "Hi there"), ("user", "How are you?")]:
        log = ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
        )
        logs.append(log)

    formatted = ChatHistoryService.format_for_prompt(logs)

    # Should be chronological with You/Them labels
    lines = formatted.split("\n")
    assert len(lines) == 3
    assert "You: Hello" in formatted
    assert "Them: Hi there" in formatted
    assert "You: How are you?" in formatted
