"""
Tests for ChatToneLearnerService - per-chat tone profile learning.
"""

import pytest
from app.database import SessionLocal
from app.models.user import User
from app.models.chat_config import ChatConfig
from app.models.chat_message_log import ChatMessageLog
from app.models.chat_tone_profile import ChatToneProfile
from app.services.chat_history_service import ChatHistoryService
from app.services.chat_tone_learner import ChatToneLearnerService


@pytest.fixture
def setup_chat_with_messages():
    """Create test data with messages in chat history."""
    db = SessionLocal()
    user = User(email="tone@example.com", password_hash="hashed", display_name="Test User")
    db.add(user)
    db.flush()

    chat = ChatConfig(
        user_id=user.id,
        chat_label="Test Chat",
        chat_type="direct"
    )
    db.add(chat)
    db.commit()

    # Add sample messages
    messages = [
        ("user", "hey how r u doing 😊", "happy"),
        ("contact", "I'm good! How about you?", "happy"),
        ("user", "all good bro! lol", "happy"),
        ("contact", "That's awesome!", "happy"),
        ("user", "yaar let's meet tomorrow", "curious"),
        ("contact", "Sure! What time?", "curious"),
        ("user", "maybe around 5pm? 🙌", "happy"),
    ]

    for role, text, mood in messages:
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role=role,
            message_text=text,
            detected_mood=mood,
        )

    yield db, user, chat

    # Cleanup
    db.query(ChatToneProfile).delete()
    db.query(ChatMessageLog).delete()
    db.query(ChatConfig).delete()
    db.query(User).delete()
    db.commit()
    db.close()


def test_extract_slang_patterns():
    """Test slang pattern extraction."""
    text = "hey bro, ngl this is cool, fr fr, lol"
    slang = ChatToneLearnerService.extract_slang_patterns(text)

    assert "bro" in slang
    assert "ngl" in slang
    assert "fr" in slang
    assert "lol" in slang


def test_extract_emojis():
    """Test emoji extraction."""
    text = "Hey there! 😊 How are you? 👋 That's awesome! 🎉"
    emojis = ChatToneLearnerService.extract_emojis(text)

    assert len(emojis) >= 3
    assert "😊" in emojis
    assert "👋" in emojis


def test_calculate_avg_message_length(setup_chat_with_messages):
    """Test average message length calculation."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    avg_length = ChatToneLearnerService.calculate_avg_message_length(user_messages)

    # User messages are relatively short in this test set
    assert avg_length > 0
    assert avg_length < 20  # Should be relatively short


def test_calculate_emoji_frequency(setup_chat_with_messages):
    """Test emoji frequency calculation."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    freq = ChatToneLearnerService.calculate_emoji_frequency(user_messages)

    # Should be between 0 and 1
    assert 0.0 <= freq <= 1.0


def test_get_common_emojis(setup_chat_with_messages):
    """Test common emoji extraction."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    common_emojis = ChatToneLearnerService.get_common_emojis(user_messages, limit=3)

    # Should return list of emojis
    assert isinstance(common_emojis, list)


def test_get_slang_patterns(setup_chat_with_messages):
    """Test common slang pattern extraction."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    slang = ChatToneLearnerService.get_slang_patterns(user_messages, limit=5)

    # Should extract slang like 'bro', 'lol', 'yaar'
    assert isinstance(slang, list)
    assert any(s in ["bro", "lol", "yaar"] for s in slang)


def test_detect_punctuation_style(setup_chat_with_messages):
    """Test punctuation style detection."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    style = ChatToneLearnerService.detect_punctuation_style(user_messages)

    # Should be one of the defined styles
    assert style in ["expressive", "calm", "balanced", "unknown"]


def test_detect_caps_usage(setup_chat_with_messages):
    """Test caps usage detection."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    caps_usage = ChatToneLearnerService.detect_caps_usage(user_messages)

    # Should be one of the defined patterns
    assert caps_usage in ["lowercase", "frequent", "mixed", "unknown"]


def test_detect_language_mix(setup_chat_with_messages):
    """Test language mix detection."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    languages = ChatToneLearnerService.detect_language_mix(user_messages)

    # Should detect English at least
    assert isinstance(languages, list)
    assert "English" in languages


def test_get_message_openers(setup_chat_with_messages):
    """Test message opener patterns."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    openers = ChatToneLearnerService.get_message_openers(user_messages, limit=3)

    # Should return list of opening words
    assert isinstance(openers, list)
    assert len(openers) > 0


def test_get_message_closers(setup_chat_with_messages):
    """Test message closer patterns."""
    db, user, chat = setup_chat_with_messages

    user_messages = ChatHistoryService.get_user_messages_only(db, chat.id, limit=100)
    closers = ChatToneLearnerService.get_message_closers(user_messages, limit=3)

    # Should return list of closing words
    assert isinstance(closers, list)


def test_learn_chat_specific_tone(setup_chat_with_messages):
    """Test learning per-chat tone profile."""
    db, user, chat = setup_chat_with_messages

    profile = ChatToneLearnerService.learn_chat_specific_tone(db, chat.id)

    assert profile.chat_config_id == chat.id
    assert profile.user_id == user.id
    assert profile.avg_message_length is not None
    assert profile.formality_score is not None
    assert profile.punctuation_style is not None
    assert profile.caps_usage is not None
    assert isinstance(profile.common_emojis, list)
    assert isinstance(profile.slang_patterns, list)


def test_compare_global_vs_chat_tone(setup_chat_with_messages):
    """Test comparison between global and chat-specific tone."""
    db, user, chat = setup_chat_with_messages

    # First, learn the chat-specific tone
    ChatToneLearnerService.learn_chat_specific_tone(db, chat.id)

    # Compare with global tone (which may not exist)
    comparison = ChatToneLearnerService.compare_global_vs_chat_tone(db, user.id, chat.id)

    assert "avg_message_length" in comparison
    assert "emoji_frequency" in comparison
    assert "formality_score" in comparison


def test_learn_from_empty_chat(setup_chat_with_messages):
    """Test learning tone from a chat with no messages."""
    db, user, chat = setup_chat_with_messages

    # Create a new empty chat
    empty_chat = ChatConfig(
        user_id=user.id,
        chat_label="Empty Chat",
        chat_type="direct"
    )
    db.add(empty_chat)
    db.commit()

    # Should create an empty profile without errors
    profile = ChatToneLearnerService.learn_chat_specific_tone(db, empty_chat.id)

    assert profile.chat_config_id == empty_chat.id
    assert profile.avg_message_length is None or profile.avg_message_length == 0.0


def test_formality_score_calculation():
    """Test formality score calculation."""
    formal_text = "I would appreciate your assistance. Kindly provide the requested information."
    casual_text = "hey bro, can you help me out? ngl this is urgent fr fr"

    formal_score = ChatToneLearnerService.calculate_formality_score(formal_text, 0, len(formal_text.split()))
    casual_score = ChatToneLearnerService.calculate_formality_score(casual_text, 5, len(casual_text.split()))

    # Formal should have higher score
    assert formal_score > casual_score
    assert 1.0 <= formal_score <= 5.0
    assert 1.0 <= casual_score <= 5.0
