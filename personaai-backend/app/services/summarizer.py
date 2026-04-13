import json
import openai
from app.config import get_settings

settings = get_settings()

class SummarizerService:
    @staticmethod
    def summarize(messages: list[str]) -> tuple[str, list[str]]:
        if not settings.openai_enabled:
            preview = "; ".join(messages[:3])
            summary = f"{len(messages)} messages received. Key points: {preview}"
            action_items = [f"Reply to: {message[:40]}" for message in messages[:2]]
            return summary, action_items

        client = openai.OpenAI(api_key=settings.openai_api_key)
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
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
        
            result = json.loads(response.choices[0].message.content)
            return result.get("summary", ""), result.get("action_items", [])
        except Exception:
            return "Failed to parse summary", []
