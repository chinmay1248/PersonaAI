import json
import logging
import re
from typing import Any

from openai import OpenAI

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def create_client() -> OpenAI:
    if not settings.llm_enabled:
        raise ValueError("LLM provider is disabled")
    if settings.normalized_llm_provider == "openai" and not settings.llm_api_key:
        raise ValueError("LLM API key is missing")

    client_kwargs: dict[str, Any] = {"api_key": settings.llm_api_key or "ollama"}
    if settings.resolved_llm_base_url:
        client_kwargs["base_url"] = settings.resolved_llm_base_url
    return OpenAI(**client_kwargs)


def _extract_json_candidate(content: str) -> str:
    candidate = content.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
        candidate = re.sub(r"\s*```$", "", candidate)
    return candidate.strip()


def parse_json_response(content: Any) -> dict[str, Any] | None:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        candidate = _extract_json_candidate(content)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start != -1 and end > start:
                try:
                    return json.loads(candidate[start : end + 1])
                except json.JSONDecodeError:
                    pass
            logger.warning("Unable to parse LLM response as JSON: %s", content)
            return None
    return None


def create_chat_completion(model: str, messages: list[dict[str, str]], **kwargs: Any):
    if not settings.llm_enabled:
        return None
    try:
        client = create_client()
        request_kwargs = dict(kwargs)
        if settings.normalized_llm_provider == "ollama":
            request_kwargs.pop("response_format", None)
        return client.chat.completions.create(model=model, messages=messages, **request_kwargs)
    except Exception as exc:
        logger.warning("%s chat completion failed: %s", settings.normalized_llm_provider, exc)
        return None


def create_embeddings(input: str | list[str], model: str | None = None):
    if not settings.llm_enabled:
        return None
    try:
        client = create_client()
        return client.embeddings.create(input=input, model=model or settings.resolved_embedding_model)
    except Exception as exc:
        logger.warning("%s embeddings request failed: %s", settings.normalized_llm_provider, exc)
        return None
