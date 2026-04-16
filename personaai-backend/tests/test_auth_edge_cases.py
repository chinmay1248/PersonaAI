"""
Test edge cases and error handling in authentication.
"""

import pytest
from app.services.auth_service import AuthService, pwd_context
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.database import SessionLocal


def test_register_duplicate_email():
    """Test that registering with existing email fails."""
    db = SessionLocal()
    
    try:
        # Register first user
        payload1 = RegisterRequest(
            email="duplicate@test.com",
            password="Pass123!Pass123!",
            display_name="First User"
        )
        user1 = AuthService.register_user(db, payload1)
        assert user1 is not None
        
        # Try to register with same email
        payload2 = RegisterRequest(
            email="duplicate@test.com",
            password="DiffPass456!",
            display_name="Second User"
        )
        with pytest.raises(ValueError):
            AuthService.register_user(db, payload2)
    finally:
        db.query(User).filter(User.email == "duplicate@test.com").delete()
        db.commit()
        db.close()


def test_login_with_wrong_password():
    """Test that login fails with incorrect password."""
    db = SessionLocal()
    
    try:
        # Create user
        reg_payload = RegisterRequest(
            email="wrongpass@test.com",
            password="CorrectPass123!",
            display_name="Test User"
        )
        AuthService.register_user(db, reg_payload)
        
        # Try to login with wrong password
        login_payload = LoginRequest(
            email="wrongpass@test.com",
            password="WrongPass456!"
        )
        with pytest.raises(ValueError):
            AuthService.login_user(db, login_payload)
    finally:
        db.query(User).filter(User.email == "wrongpass@test.com").delete()
        db.commit()
        db.close()


def test_login_nonexistent_user():
    """Test that login fails for non-existent users."""
    db = SessionLocal()
    
    try:
        login_payload = LoginRequest(
            email="nonexistent@test.com",
            password="AnyPassword123!"
        )
        with pytest.raises(ValueError):
            AuthService.login_user(db, login_payload)
    finally:
        db.close()


def test_successful_login():
    """Test successful user login."""
    db = SessionLocal()
    
    try:
        # Create user
        reg_payload = RegisterRequest(
            email="login@test.com",
            password="CorrectPass123!",
            display_name="Test User"
        )
        user = AuthService.register_user(db, reg_payload)
        assert user is not None
        assert user.access_token
        assert user.refresh_token
        
        # Login with correct password
        login_payload = LoginRequest(
            email="login@test.com",
            password="CorrectPass123!"
        )
        result = AuthService.login_user(db, login_payload)
        assert result is not None
        assert result.access_token
        assert result.refresh_token
        assert result.user_id == user.user_id
    finally:
        db.query(User).filter(User.email == "login@test.com").delete()
        db.commit()
        db.close()


def test_password_hash_consistency():
    """Test that password hashing is deterministic and verifiable."""
    password = "TestPassword123!"
    hash1 = pwd_context.hash(password)
    
    # Verify the hash matches the password
    assert pwd_context.verify(password, hash1)
    
    # Verify wrong password doesn't match
    assert not pwd_context.verify("WrongPassword", hash1)
    
    # Hashes should be different each time (bcrypt with salt)
    hash2 = pwd_context.hash(password)
    assert hash1 != hash2
    assert pwd_context.verify(password, hash2)


def test_register_with_strong_password():
    """Test registering user with strong password."""
    db = SessionLocal()
    
    try:
        payload = RegisterRequest(
            email="strong@test.com",
            password="VeryStr0ng!P@ssw0rd#2024",
            display_name="Security Conscious User"
        )
        user = AuthService.register_user(db, payload)
        assert user is not None
        assert user.user_id
    finally:
        db.query(User).filter(User.email == "strong@test.com").delete()
        db.commit()
        db.close()


def test_register_response_has_tokens():
    """Test that register response includes tokens."""
    db = SessionLocal()
    
    try:
        payload = RegisterRequest(
            email="tokens@test.com",
            password="Pass123!Pass123!",
            display_name="Token User"
        )
        response = AuthService.register_user(db, payload)
        
        assert response.user_id is not None
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in > 0
    finally:
        db.query(User).filter(User.email == "tokens@test.com").delete()
        db.commit()
        db.close()
