import re

from app.config import get_settings
from app.services.openai_client import create_chat_completion, parse_json_response

settings = get_settings()

class SummarizerService:
    @staticmethod
    def summarize(messages: list[str]) -> tuple[str, list[str]]:
        clean_messages = [" ".join(str(message).split()) for message in messages if str(message).strip()]
        if not clean_messages:
            return "No messages available to summarize.", []

        if not settings.llm_enabled:
            return SummarizerService._fallback_summary(clean_messages)

        combined = "\n".join(f"- {msg}" for msg in clean_messages)
        response = create_chat_completion(
            model=settings.resolved_chat_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You summarize chat conversations. Return a compact JSON object with keys "
                        "\"summary\" and \"action_items\". "
                        "\"summary\" must be a short, natural overview. "
                        "\"action_items\" must be an array of concrete follow-ups inferred from the chat. "
                        "If there are no clear action items, return an empty array."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Summarize this chat and identify the action items.\n\n"
                        f"Messages:\n{combined}"
                    ),
                },
            ],
            max_tokens=300,
            temperature=0.3,
        )

        if not response or not response.choices:
            return SummarizerService._fallback_summary(clean_messages)

        content = response.choices[0].message.content
        result = parse_json_response(content)
        if isinstance(result, dict):
            summary = " ".join(str(result.get("summary", "")).split())
            action_items = [item for item in result.get("action_items", []) if str(item).strip()]
            if summary:
                return summary, action_items[:5]

        plain_summary = SummarizerService._parse_plain_summary(content)
        if plain_summary:
            return plain_summary

        return SummarizerService._fallback_summary(clean_messages)

    @staticmethod
    def _fallback_summary(messages: list[str]) -> tuple[str, list[str]]:
        latest_messages = messages[-5:]
        summary = "Conversation is about: " + "; ".join(message[:80] for message in latest_messages[:3])
        action_items = []
        for message in latest_messages:
            lowered = message.lower()
            if "?" in message or any(keyword in lowered for keyword in {"send", "share", "call", "meet", "check", "reply", "confirm"}):
                action_items.append(message[:80])
        return summary, action_items[:5]

    @staticmethod
    def _parse_plain_summary(content: str) -> tuple[str, list[str]] | None:
        text = " ".join(str(content or "").split()).strip()
        if not text:
            return None

        action_items: list[str] = []
        if "action item" in text.lower():
            sections = re.split(r"action items?:", text, flags=re.IGNORECASE)
            summary = sections[0].strip(" -:")
            if len(sections) > 1:
                action_items = [
                    item.strip(" -")
                    for item in re.split(r"[;\n]", sections[1])
                    if item.strip(" -")
                ][:5]
            return (summary, action_items) if summary else None

        return text[:300], []
