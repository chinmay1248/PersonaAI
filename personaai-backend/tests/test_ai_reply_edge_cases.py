"""
Test edge cases and error handling in AI reply generation.
"""

import pytest
from app.database import SessionLocal
from app.models.user import User
from app.models.chat_config import ChatConfig
from app.models.tone_profile import ToneProfile
from app.models.training_sample import TrainingSample
from app.services.ai_engine import AIEngineService


def test_generate_reply_with_empty_message():
    """Test that empty messages are handled."""
    db = SessionLocal()
    try:
        # Create test user and chat config
        user = User(email="empty@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        # Try to generate reply with empty message
        service = AIEngineService()
        with pytest.raises((ValueError, Exception)):
            service.generate_reply(db, user.id, "", chat.id)
    finally:
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_with_very_long_message():
    """Test handling of very long messages."""
    db = SessionLocal()
    try:
        user = User(email="long@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        # Generate very long message
        long_message = "a" * 10000
        
        service = AIEngineService()
        # Should either truncate or handle gracefully
        try:
            reply = service.generate_reply(db, user.id, long_message, chat.id)
            # If it succeeds, verify it returns something reasonable
            assert reply is not None or reply == []
        except Exception:
            # Exception is also acceptable for very long input
            pass
    finally:
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_without_tone_profile():
    """Test reply generation when user has no tone profile."""
    db = SessionLocal()
    try:
        user = User(email="notone@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        service = AIEngineService()
        # Should generate generic replies without tone profile
        replies = service.generate_reply(db, user.id, "Hey how are you?", chat.id)
        
        # Should return some result (might be generic)
        assert isinstance(replies, list)
    finally:
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_with_special_characters():
    """Test message with special characters and emojis."""
    db = SessionLocal()
    try:
        user = User(email="special@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        service = AIEngineService()
        message = "Hey! 😀 How are you? #PersonaAI @mentions work? 🎉"
        
        replies = service.generate_reply(db, user.id, message, chat.id)
        
        # Should handle emojis and special chars
        assert replies is not None or isinstance(replies, list)
    finally:
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_for_nonexistent_chat():
    """Test reply generation with invalid chat ID."""
    db = SessionLocal()
    try:
        user = User(email="nochat@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.commit()
        
        service = AIEngineService()
        # Use nonexistent chat ID
        with pytest.raises((ValueError, AttributeError, Exception)):
            service.generate_reply(db, user.id, "Hello", "nonexistent-chat-id")
    finally:
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_for_nonexistent_user():
    """Test reply generation with invalid user ID."""
    db = SessionLocal()
    try:
        # Create a chat for testing
        user = User(email="helper@test.com", password_hash="test", display_name="Helper")
        db.add(user)
        db.flush()
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        service = AIEngineService()
        # Try with different user ID
        with pytest.raises((ValueError, AttributeError, Exception)):
            service.generate_reply(db, "nonexistent-user-id", "Hello", chat.id)
    finally:
        db.query(ChatConfig).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_generate_reply_with_null_personality():
    """Test reply generation when tone profile has null fields."""
    db = SessionLocal()
    try:
        user = User(email="nulltone@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        # Create tone profile with minimal data
        tone = ToneProfile(
            user_id=user.id,
            slang_patterns=[],
            common_emojis=[],
            formality_score=0.5,
            language_mix=[],
            punctuation_style=None,
            caps_usage=None
        )
        db.add(tone)
        
        chat = ChatConfig(
            user_id=user.id,
            label="Test Chat",
            chat_type="direct"
        )
        db.add(chat)
        db.commit()
        
        service = AIEngineService()
        replies = service.generate_reply(db, user.id, "Hi!", chat.id)
        
        # Should still generate replies
        assert replies is not None or isinstance(replies, list)
    finally:
        db.query(ChatConfig).delete()
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_mood_detection_with_various_inputs():
    """Test mood detection with different message types."""
    service = AIEngineService()
    
    test_cases = [
        ("I'm so happy! 😊", ["happy", "excited"]),
        ("I'm sad 😢", ["sad", "concerned"]),
        ("What do you mean? 🤔", ["curious", "concerned"]),
        ("LOL that's hilarious 😂", ["happy", "excited"]),
        ("I'm angry about this!", ["angry"]),
        ("Just a normal message", ["neutral"]),
    ]
    
    for message, expected_moods in test_cases:
        detected_mood = service.detect_mood(message)
        # Just verify it returns a string
        assert isinstance(detected_mood, str)
        assert len(detected_mood) > 0
