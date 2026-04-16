"""
Test edge cases in tone profile training.
"""

import pytest
from app.database import SessionLocal
from app.models.user import User
from app.models.tone_profile import ToneProfile
from app.models.training_sample import TrainingSample
from app.services.tone_learner import ToneLearnerService


def test_train_with_empty_samples():
    """Test tone training with empty sample list."""
    db = SessionLocal()
    try:
        user = User(email="empty@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        
        # Empty samples list
        with pytest.raises((ValueError, Exception)):
            service.train(db, user.id, [])
    finally:
        db.query(User).delete()
        db.commit()
        db.close()


def test_train_with_single_sample():
    """Test tone training with only one sample."""
    db = SessionLocal()
    try:
        user = User(email="single@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        samples = ["hey whats up bro"]
        
        # Should handle single sample gracefully
        result = service.train(db, user.id, samples)
        assert result is not None
        
        # Verify tone profile was created or updated
        tone = db.query(ToneProfile).filter(ToneProfile.user_id == user.id).one_or_none()
        assert tone is not None
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_train_with_duplicate_samples():
    """Test tone training with duplicate messages."""
    db = SessionLocal()
    try:
        user = User(email="dups@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        samples = ["hey", "hey", "hey", "hey how are you", "hey"]
        
        # Should handle duplicates without crashing
        result = service.train(db, user.id, samples)
        assert result is not None
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_train_with_very_short_samples():
    """Test tone training with very short messages."""
    db = SessionLocal()
    try:
        user = User(email="short@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        samples = ["hi", "ok", "lol", "yep", "nope", "cool", "nice"]
        
        # Should handle short messages
        result = service.train(db, user.id, samples)
        assert result is not None
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_train_with_very_long_samples():
    """Test tone training with very long messages."""
    db = SessionLocal()
    try:
        user = User(email="long@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        long_message = "This is a very long message that goes on and on. " * 50
        samples = [long_message]
        
        # Should handle long messages (might truncate)
        result = service.train(db, user.id, samples)
        assert result is not None
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_train_from_messages_for_nonexistent_user():
    """Test training with invalid user ID."""
    db = SessionLocal()
    try:
        service = ToneLearnerService()
        
        # Use nonexistent user ID
        with pytest.raises((ValueError, AttributeError, Exception)):
            service.train_from_messages(db, "nonexistent-user-id", ["hello"], "test")
    finally:
        db.close()


def test_retrain_overwrites_previous_profile():
    """Test that retraining updates the existing tone profile."""
    db = SessionLocal()
    try:
        user = User(email="retrain@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        service = ToneLearnerService()
        
        # First training
        samples1 = ["hey bro", "yo what up", "let's go"]
        result1 = service.train(db, user.id, samples1)
        
        tone1 = db.query(ToneProfile).filter(ToneProfile.user_id == user.id).one()
        id1 = tone1.id
        
        # Second training
        samples2 = ["formal greeting", "how do you do", "good afternoon"]
        result2 = service.train(db, user.id, samples2)
        
        tone2 = db.query(ToneProfile).filter(ToneProfile.user_id == user.id).one()
        id2 = tone2.id
        
        # Should be the same profile (updated, not new)
        assert id1 == id2
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_extract_slang_patterns():
    """Test slang pattern extraction."""
    service = ToneLearnerService()
    
    samples = [
        "yo what's good",
        "that's lit fam",
        "no cap that's fire",
        "lowkey that was sus",
    ]
    
    patterns = service._extract_slang_patterns(samples)
    
    # Should find some patterns
    assert isinstance(patterns, list)
    # Should contain some slang terms
    assert any("yo" in str(p).lower() or "lit" in str(p).lower() or "fire" in str(p).lower() 
               for p in patterns)


def test_extract_emoji_frequency():
    """Test emoji frequency extraction."""
    service = ToneLearnerService()
    
    samples = [
        "hey 😀 how are you",
        "that's 😀😀 awesome",
        "love it 😍",
        "🎉🎉🎉 party time",
    ]
    
    emojis, frequency = service._extract_emoji_patterns(samples)
    
    # Should find emojis
    assert isinstance(emojis, list)
    assert isinstance(frequency, float)
    assert 0 <= frequency <= 1


def test_analyze_formality():
    """Test formality score calculation."""
    service = ToneLearnerService()
    
    casual = ["yo", "hey bro", "nah nah", "lol ok"]
    formal = ["Good morning", "How do you do", "I appreciate your inquiry"]
    
    casual_score = service._analyze_formality(casual)
    formal_score = service._analyze_formality(formal)
    
    # Casual should be lower than formal
    assert casual_score < formal_score
    assert 0 <= casual_score <= 1
    assert 0 <= formal_score <= 1


def test_detect_language_mix():
    """Test language mix detection."""
    service = ToneLearnerService()
    
    # English only
    english = ["hello", "how are you", "what's up"]
    eng_mix = service._detect_language_mix(english)
    assert "english" in [l.lower() for l in eng_mix]
    
    # Mixed languages
    mixed = ["hello", "namaste", "hola", "привет"]
    mixed_mix = service._detect_language_mix(mixed)
    assert len(mixed_mix) > 0


def test_tone_profile_accuracy_score():
    """Test that tone profile has accuracy score."""
    db = SessionLocal()
    try:
        user = User(email="accuracy@test.com", password_hash="test", display_name="Tester")
        db.add(user)
        db.flush()
        
        tone = ToneProfile(
            user_id=user.id,
            slang_patterns=[],
            common_emojis=[],
            formality_score=0.6,
            accuracy_score=0.75  # Set accuracy
        )
        db.add(tone)
        db.commit()
        
        fetched = db.query(ToneProfile).filter(ToneProfile.user_id == user.id).one()
        assert hasattr(fetched, 'accuracy_score')
        assert fetched.accuracy_score == 0.75
    finally:
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()
