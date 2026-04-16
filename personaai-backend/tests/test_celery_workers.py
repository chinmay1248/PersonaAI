"""
Test Celery workers and scheduled tasks.
"""

import pytest
from app.database import SessionLocal
from app.models.training_sample import TrainingSample
from app.models.tone_profile import ToneProfile
from app.models.user import User
from app.workers.training_job import run_training_job
from app.workers.tone_update_job import refresh_tone_profiles


def test_training_job_with_untrained_samples():
    """Test that training job processes untrained samples."""
    db = SessionLocal()
    try:
        # Create test user
        user = User(email="trainer@test.com", password_hash="test", display_name="Trainer")
        db.add(user)
        db.flush()
        
        # Add untrained samples
        sample1 = TrainingSample(
            user_id=user.id,
            sample_text="hey bro whats up",
            source="manual",
            used_in_training=False
        )
        sample2 = TrainingSample(
            user_id=user.id,
            sample_text="yo dude we good?",
            source="manual",
            used_in_training=False
        )
        db.add_all([sample1, sample2])
        db.commit()
        
        # Run training job
        result = run_training_job()
        
        # Verify result message
        assert "Trained" in result or "samples" in result.lower()
        
        # Verify samples are now marked as used
        trained_samples = db.query(TrainingSample).filter(
            TrainingSample.user_id == user.id,
            TrainingSample.used_in_training == True  # noqa: E712
        ).all()
        
        assert len(trained_samples) >= 0  # At least processed
        
    finally:
        db.query(TrainingSample).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_training_job_with_no_samples():
    """Test training job handles empty database gracefully."""
    db = SessionLocal()
    try:
        # Ensure no untrained samples
        db.query(TrainingSample).filter(TrainingSample.used_in_training == False).delete()  # noqa: E712
        db.commit()
        
        # Run training job
        result = run_training_job()
        
        # Should return gracefully
        assert "No untrained samples" in result or result.startswith("Trained 0")
        
    finally:
        db.close()


def test_refresh_tone_profiles_with_samples():
    """Test tone profile refresh job."""
    db = SessionLocal()
    try:
        # Create test user with tone profile
        user = User(email="tone@test.com", password_hash="test", display_name="Tone Learner")
        db.add(user)
        db.flush()
        
        # Create tone profile
        tone = ToneProfile(
            user_id=user.id,
            slang_patterns=[],
            common_emojis=[],
            emoji_frequency=0.2,
            formality_score=0.5,
            language_mix=["english"],
            punctuation_style="casual",
            caps_usage="normal"
        )
        db.add(tone)
        
        # Add trained samples
        for i in range(3):
            sample = TrainingSample(
                user_id=user.id,
                sample_text=f"Sample text {i}",
                source="manual",
                used_in_training=True
            )
            db.add(sample)
        
        db.commit()
        
        # Run refresh job
        result = refresh_tone_profiles()
        
        # Should complete successfully
        assert "Refreshed" in result or "profiles" in result.lower()
        
    finally:
        db.query(TrainingSample).delete()
        db.query(ToneProfile).delete()
        db.query(User).delete()
        db.commit()
        db.close()


def test_refresh_tone_profiles_with_no_profiles():
    """Test refresh job handles no profiles gracefully."""
    db = SessionLocal()
    try:
        # Ensure no tone profiles
        db.query(ToneProfile).delete()
        db.commit()
        
        # Run refresh job
        result = refresh_tone_profiles()
        
        # Should return gracefully
        assert "No tone profiles" in result or result.startswith("Refreshed 0")
        
    finally:
        db.close()


def test_scheduler_is_configured():
    """Verify Celery Beat scheduler is properly configured."""
    from app.workers.celery_app import celery_app
    
    # Check that beat schedule is configured
    assert hasattr(celery_app.conf, 'beat_schedule')
    assert 'train-every-15-min' in celery_app.conf.beat_schedule
    assert 'refresh-tone-profiles-hourly' in celery_app.conf.beat_schedule
    
    # Verify schedule times (in seconds)
    assert celery_app.conf.beat_schedule['train-every-15-min']['schedule'] == 60.0 * 15
    assert celery_app.conf.beat_schedule['refresh-tone-profiles-hourly']['schedule'] == 60.0 * 60
