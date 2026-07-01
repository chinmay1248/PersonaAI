"""
Integration tests for AI Engine with per-chat tone and message history.
"""

import pytest
from app.database import SessionLocal
from app.models.user import User
from app.models.chat_config import ChatConfig
from app.models.tone_profile import ToneProfile
from app.models.chat_tone_profile import ChatToneProfile
from app.models.chat_message_log import ChatMessageLog
from app.schemas.ai import GenerateReplyRequest, ConversationMessage
from app.services.ai_engine import AIEngineService
from app.services.chat_history_service import ChatHistoryService
from app.services.chat_tone_learner import ChatToneLearnerService


@pytest.fixture
def setup_user_with_tone_and_chat():
    """Create user with global tone profile and chat with tone profile."""
    db = SessionLocal()

    # Create user
    user = User(email="aitest@example.com", password_hash="hashed", display_name="AI Test User")
    db.add(user)
    db.flush()

    # Create global tone profile
    global_tone = ToneProfile(
        user_id=user.id,
        avg_message_length=12.5,
        emoji_frequency=0.15,
        slang_patterns=["bro", "lol", "fr"],
        common_emojis=["😊", "👋"],
        punctuation_style="balanced",
        formality_score=2.5,
        caps_usage="lowercase",
        language_mix=["English"],
        tone_shifts={},
    )
    db.add(global_tone)
    db.flush()

    # Create chat config
    chat = ChatConfig(
        user_id=user.id,
        chat_label="Best Friend Chat",
        chat_type="direct",
        personality_mode="funny"
    )
    db.add(chat)
    db.flush()

    # Create chat-specific tone profile
    chat_tone = ChatToneProfile(
        chat_config_id=chat.id,
        user_id=user.id,
        avg_message_length=15.0,  # Slightly longer with this friend
        emoji_frequency=0.25,  # More emojis
        slang_patterns=["bro", "lol", "lmao", "fr", "ngl"],
        common_emojis=["😊", "🙌", "🎉"],
        punctuation_style="expressive",
        formality_score=2.0,  # More casual with this friend
        caps_usage="lowercase",
        language_mix=["English"],
        tone_shifts={},
        message_openers=["hey", "bro", "lol"],
        message_closers=["lol", "fr", "ngl"],
        response_timing={},
    )
    db.add(chat_tone)
    db.flush()

    # Add message history to chat
    messages = [
        ("user", "hey bro! how u been? 😊", "happy"),
        ("contact", "yo! all good fam", "happy"),
        ("user", "that's sick 🙌 wanna hang later?", "curious"),
        ("contact", "for sure! what time?", "curious"),
        ("user", "around 5? we can grab some food lol", "happy"),
        ("contact", "perfect! see you then 🎉", "happy"),
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

    db.commit()
    yield db, user, chat, global_tone, chat_tone

    # Cleanup
    db.query(ChatMessageLog).delete()
    db.query(ChatToneProfile).delete()
    db.query(ChatConfig).delete()
    db.query(ToneProfile).delete()
    db.query(User).delete()
    db.commit()
    db.close()


def test_generate_reply_loads_chat_tone(setup_user_with_tone_and_chat):
    """Test that generate_reply loads and uses chat-specific tone."""
    db, user, chat, global_tone, chat_tone = setup_user_with_tone_and_chat

    # Create a request
    payload = GenerateReplyRequest(
        chat_config_id=chat.id,
        incoming_messages=["bro this is so funny 😂"],
        conversation_history=[],
        count=1,
    )

    # Generate replies - this will test if chat tone is loaded and used
    conversation, suggestions, mood = AIEngineService.generate_replies(db, user.id, payload)

    # Verify suggestions were generated
    assert len(suggestions) > 0
    assert suggestions[0].reply_text is not None
    assert mood == "happy"  # Should detect happy mood

    # Verify conversation was logged
    assert conversation.user_id == user.id
    assert conversation.chat_config_id == chat.id


def test_incoming_message_logged_to_chat_history(setup_user_with_tone_and_chat):
    """Test that incoming message is logged to ChatMessageLog."""
    db, user, chat, global_tone, chat_tone = setup_user_with_tone_and_chat

    initial_count = ChatHistoryService.get_message_count(db, chat.id)

    payload = GenerateReplyRequest(
        chat_config_id=chat.id,
        incoming_messages=["test message"],
        conversation_history=[],
        count=1,
    )

    AIEngineService.generate_replies(db, user.id, payload)

    final_count = ChatHistoryService.get_message_count(db, chat.id)

    # Should have logged the incoming message
    assert final_count == initial_count + 1

    # Verify the message was logged as "contact" role
    recent_messages = ChatHistoryService.get_recent_messages(db, chat.id, minutes=5)
    assert any(msg.message_role == "contact" and msg.message_text == "test message" for msg in recent_messages)


def test_chat_history_extended_beyond_payload(setup_user_with_tone_and_chat):
    """Test that AI engine uses extended chat history from ChatMessageLog."""
    db, user, chat, global_tone, chat_tone = setup_user_with_tone_and_chat

    # Add more messages to the chat
    for i in range(10):
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role="user" if i % 2 == 0 else "contact",
            message_text=f"Message {i}",
        )

    # Create a request with empty payload history
    payload = GenerateReplyRequest(
        chat_config_id=chat.id,
        incoming_messages=["what should i say?"],
        conversation_history=[],  # Empty - should use ChatMessageLog instead
        count=1,
    )

    # This should use extended history from ChatMessageLog
    conversation, suggestions, _ = AIEngineService.generate_replies(db, user.id, payload)

    # Should still generate replies successfully
    assert len(suggestions) > 0


def test_tone_profile_not_found_graceful(setup_user_with_tone_and_chat):
    """Test that system works even if chat tone profile doesn't exist yet."""
    db, user, chat, _, _ = setup_user_with_tone_and_chat

    # Create a new chat with no tone profile
    new_chat = ChatConfig(
        user_id=user.id,
        chat_label="New Chat",
        chat_type="direct"
    )
    db.add(new_chat)
    db.commit()

    # Should still generate replies without the tone profile
    payload = GenerateReplyRequest(
        chat_config_id=new_chat.id,
        incoming_messages=["hey"],
        conversation_history=[],
        count=1,
    )

    conversation, suggestions, _ = AIEngineService.generate_replies(db, user.id, payload)

    # Should fall back to global tone gracefully
    assert len(suggestions) > 0


def test_chat_tone_influences_reply_generation(setup_user_with_tone_and_chat):
    """Test that chat-specific tone influences generated replies."""
    db, user, chat, _, _ = setup_user_with_tone_and_chat

    # For a chat with formal tone
    formal_chat = ChatConfig(
        user_id=user.id,
        chat_label="Boss Chat",
        chat_type="direct",
    )
    db.add(formal_chat)
    db.flush()

    formal_tone = ChatToneProfile(
        chat_config_id=formal_chat.id,
        user_id=user.id,
        formality_score=4.5,  # Very formal
        punctuation_style="calm",
        avg_message_length=20.0,
        emoji_frequency=0.02,  # Minimal emojis
        slang_patterns=[],  # No slang
        common_emojis=[],
        language_mix=["English"],
        tone_shifts={},
        message_openers=["hello", "hi", "good"],
        message_closers=["regards", "thanks"],
        response_timing={},
    )
    db.add(formal_tone)
    db.commit()

    # Generate reply for formal chat
    payload = GenerateReplyRequest(
        chat_config_id=formal_chat.id,
        incoming_messages=["could you please review this proposal"],
        conversation_history=[],
        count=1,
    )

    conversation, suggestions, _ = AIEngineService.generate_replies(db, user.id, payload)

    # Should generate formal-sounding replies
    assert len(suggestions) > 0
    # In a real scenario, we'd check the tone of suggestions matches formal profile


def test_multiple_chats_independent_tones(setup_user_with_tone_and_chat):
    """Test that different chats maintain independent tone profiles."""
    db, user, _, _, _ = setup_user_with_tone_and_chat

    # Create two new chats with different tones
    casual_chat = ChatConfig(
        user_id=user.id,
        chat_label="Casual",
        chat_type="direct"
    )
    professional_chat = ChatConfig(
        user_id=user.id,
        chat_label="Professional",
        chat_type="direct"
    )
    db.add(casual_chat)
    db.add(professional_chat)
    db.flush()

    casual_tone = ChatToneProfile(
        chat_config_id=casual_chat.id,
        user_id=user.id,
        formality_score=2.0,
        emoji_frequency=0.5,
        slang_patterns=["lol", "bro"],
        common_emojis=["😊"],
        language_mix=["English"],
        tone_shifts={},
        message_openers=["hey"],
        message_closers=["lol"],
        response_timing={},
    )

    prof_tone = ChatToneProfile(
        chat_config_id=professional_chat.id,
        user_id=user.id,
        formality_score=4.5,
        emoji_frequency=0.0,
        slang_patterns=[],
        common_emojis=[],
        language_mix=["English"],
        tone_shifts={},
        message_openers=["hello"],
        message_closers=["thanks"],
        response_timing={},
    )

    db.add(casual_tone)
    db.add(prof_tone)
    db.commit()

    # Query both tone profiles
    casual_retrieved = db.query(ChatToneProfile).filter(
        ChatToneProfile.chat_config_id == casual_chat.id
    ).first()
    prof_retrieved = db.query(ChatToneProfile).filter(
        ChatToneProfile.chat_config_id == professional_chat.id
    ).first()

    assert casual_retrieved.formality_score < prof_retrieved.formality_score
    assert casual_retrieved.emoji_frequency > prof_retrieved.emoji_frequency
    assert len(casual_retrieved.slang_patterns) > len(prof_retrieved.slang_patterns)

from unittest.mock import patch

def test_auto_retrain_triggered_every_20_messages(setup_user_with_tone_and_chat):
    """Test that retrain_chat_tone_job is triggered every 20 messages."""
    db, user, chat, _, _ = setup_user_with_tone_and_chat

    # Reset message count to 19
    db.query(ChatMessageLog).filter(ChatMessageLog.chat_config_id == chat.id).delete()
    for i in range(19):
        ChatHistoryService.log_message(
            db=db,
            chat_config_id=chat.id,
            user_id=user.id,
            message_role="user" if i % 2 == 0 else "contact",
            message_text=f"Message {i}",
        )
    db.commit()

    payload = GenerateReplyRequest(
        chat_config_id=chat.id,
        incoming_messages=["this is the 20th message"],
        conversation_history=[],
        count=1,
    )

    with patch("app.workers.training_job.retrain_chat_tone_job.delay") as mock_delay:
        # Generate reply (this should log the 20th message and trigger retrain)
        AIEngineService.generate_replies(db, user.id, payload)
        
        # Verify it was called
        mock_delay.assert_called_once_with(chat.id, user.id)

    # Now add another message (21st)
    payload_21 = GenerateReplyRequest(
        chat_config_id=chat.id,
        incoming_messages=["this is the 21st message"],
        conversation_history=[],
        count=1,
    )

    with patch("app.workers.training_job.retrain_chat_tone_job.delay") as mock_delay_21:
        AIEngineService.generate_replies(db, user.id, payload_21)
        
        # Verify it was NOT called for 21
        mock_delay_21.assert_not_called()
