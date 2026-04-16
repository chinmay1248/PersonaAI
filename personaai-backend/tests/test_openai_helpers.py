from app.config import get_settings
from app.services.openai_client import create_chat_completion, parse_json_response


def test_parse_json_response_handles_dict() -> None:
    payload = {"replies": ["hello", "hi"]}
    assert parse_json_response(payload) == payload


def test_parse_json_response_handles_valid_json_string() -> None:
    json_text = '{"replies": ["hello", "hi"]}'
    assert parse_json_response(json_text) == {"replies": ["hello", "hi"]}


def test_parse_json_response_returns_none_for_invalid_json() -> None:
    assert parse_json_response("not a json object") is None


def test_create_chat_completion_returns_none_when_disabled() -> None:
    settings = get_settings()
    assert not settings.openai_enabled
    result = create_chat_completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5,
        temperature=0.0,
    )
    assert result is None
