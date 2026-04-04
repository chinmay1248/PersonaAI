from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app

client = TestClient(app)


def test_register_and_login() -> None:
    email = f"auth-{uuid4()}@example.com"
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPass123",
            "display_name": "Auth Test",
        },
    )
    assert register_response.status_code == 201
    payload = register_response.json()
    assert "access_token" in payload

    login_response = client.post(
        "/v1/auth/login",
        json={"email": email, "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["user_id"] == payload["user_id"]
