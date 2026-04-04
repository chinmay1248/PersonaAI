def build_reply_prompt(
    incoming_messages: list[str],
    personality_mode: str | None,
    detected_mood: str,
    slang_patterns: list[str],
) -> dict[str, str]:
    tone_hint = ", ".join(slang_patterns[:4]) if slang_patterns else "natural, friendly language"
    personality = personality_mode or "balanced"
    combined_message = " ".join(incoming_messages)

    return {
        "system": (
            "Reply like the user. "
            f"Personality mode: {personality}. "
            f"Detected mood: {detected_mood}. "
            f"Tone hints: {tone_hint}."
        ),
        "user": combined_message,
    }
