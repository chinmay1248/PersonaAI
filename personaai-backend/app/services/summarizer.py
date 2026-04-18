import json
from app.config import get_settings
from app.services.openai_client import create_chat_completion, parse_json_response

settings = get_settings()

class SummarizerService:
    @staticmethod
    def summarize(messages: list[str]) -> tuple[str, list[str]]:
        if not settings.llm_enabled:
            preview = "; ".join(messages[:3])
            summary = f"{len(messages)} messages received. Key points: {preview}"
            action_items = [f"Reply to: {message[:40]}" for message in messages[:2]]
            return summary, action_items

        combined = "\n".join(f"- {msg}" for msg in messages)
        prompt = f"""Summarize these incoming messages and identify action items.
Return ONLY a valid JSON object with this exact structure, nothing else:
{{
    "summary": "2-3 sentence overview",
    "action_items": ["item 1", "item 2"]
}}

Messages:
{combined}
"""
        response = create_chat_completion(
            model=settings.resolved_chat_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        if not response or not response.choices:
            return "Failed to parse summary", []

        result = parse_json_response(response.choices[0].message.content)
        if isinstance(result, dict):
            return result.get("summary", ""), result.get("action_items", [])
        return "Failed to parse summary", []
