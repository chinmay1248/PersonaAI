import json
import logging
from typing import Any

import openai
from openai import OpenAI

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def create_client() -> OpenAI:
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is missing")
    return openai.OpenAI(api_key=settings.openai_api_key)


def parse_json_response(content: Any) -> dict[str, Any] | None:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Unable to parse OpenAI response as JSON: %s", content)
            return None
    return None


def create_chat_completion(model: str, messages: list[dict[str, str]], **kwargs: Any):
    if not settings.openai_enabled:
        return None
    try:
        client = create_client()
        return client.chat.completions.create(model=model, messages=messages, **kwargs)
    except Exception as exc:
        logger.warning("OpenAI chat completion failed: %s", exc)
        return None


def create_embeddings(input: str | list[str], model: str = "text-embedding-3-small"):
    if not settings.openai_enabled:
        return None
    try:
        client = create_client()
        return client.embeddings.create(input=input, model=model)
    except Exception as exc:
        logger.warning("OpenAI embeddings request failed: %s", exc)
        return None
