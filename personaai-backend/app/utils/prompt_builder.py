import re


HINDI_ROMAN_MARKERS = {
    "acha", "achha", "arre", "bhai", "bro", "haan", "han", "hai", "kar", "karo", "karna",
    "kya", "kyu", "kyun", "mat", "nahi", "nahi", "nhi", "pata", "scene", "sahi", "theek",
    "thik", "yaar", "sab", "tu", "tum", "mera", "meri", "apna", "abhi", "kal",
}


def build_reply_prompt(
    incoming_messages: list[str],
    conversation_history: list[dict[str, str]],
    personality_mode: str | None,
    detected_mood: str,
    slang_patterns: list[str],
    language_mix: list[str] | None = None,
    avg_message_length: float | None = None,
    common_emojis: list[str] | None = None,
    chat_tone_profile: dict | None = None,
    global_tone_profile: dict | None = None,
    detected_intent: str | None = None,
    positive_examples: list[str] | None = None,
) -> dict[str, str]:
    personality = personality_mode or "balanced"
    recent_history = conversation_history[-50:]
    language_hint = infer_preferred_language(recent_history, incoming_messages, language_mix or [])
    tone_hint = ", ".join(slang_patterns[:6]) if slang_patterns else "natural, friendly language"
    emoji_hint = ", ".join((common_emojis or [])[:3]) or "light emoji use only if it fits naturally"
    length_hint = describe_reply_length(avg_message_length)
    transcript = format_conversation_history(recent_history)
    style_examples = format_style_examples(recent_history)
    latest_sender_intent = detected_intent or "sharing an update and expecting a natural reaction"
    latest_message = "\n".join(incoming_messages)

    # Build chat-specific tone context
    chat_tone_hint = ""
    if chat_tone_profile:
        chat_tone_hint = build_chat_tone_hint(chat_tone_profile, global_tone_profile)

    # Build positive feedback examples
    feedback_examples = ""
    if positive_examples:
        feedback_examples = "\nExamples of replies the user liked in the past (try to match this style):\n"
        feedback_examples += "\n".join(f"- {ex}" for ex in positive_examples) + "\n"

    return {
        "system": (
            "You write replies for the user inside an ongoing personal chat. "
            "Your job is to sound human, context-aware, and natural, not polished or robotic. "
            f"Personality mode: {personality}. "
            f"Detected mood of the latest incoming message(s): {detected_mood}. "
            f"Likely purpose of the latest incoming message(s): {latest_sender_intent}. "
            f"Preferred language style: {language_hint}. "
            f"Tone hints from the user's past messages: {tone_hint}. "
            f"Emoji style hint: {emoji_hint}. "
            f"Preferred reply length: {length_hint}. "
            + (f"Chat-specific communication style: {chat_tone_hint} " if chat_tone_hint else "")
            + (
                "Match the language actually used in the recent conversation. "
                "If the chat is in Hindi or Hinglish, reply in Hindi or Hinglish. "
                "Use the recent conversation to understand references, plans, jokes, names, promises, and emotional tone before replying. "
                "First understand what the other person is trying to do: ask, inform, tease, plan, confirm, flirt, complain, or share something. "
                "Then reply directly to that move in the conversation. "
                "Do not answer like a customer-support bot. "
                "Do not over-explain. "
                "Do not be overly formal unless the chat is formal. "
                "Avoid generic filler like 'okay', 'sounds good', 'give me a minute', or 'haha okay' unless it truly fits the exact context. "
                "If they shared an item, photo, plan, joke, or opinion, react specifically to that thing instead of giving a vague acknowledgement. "
                "Each option should feel like a believable next text the user would actually send right now. "
                "The options should be meaningfully different in angle, but all should fit the same context. "
                "Do not mention that you analyzed the chat."
            )
        ),
        "user": (
            "Task: write reply options for the latest incoming message(s).\n\n"
            "Recent conversation history:\n"
            f"{transcript}\n\n"
            "Recent examples of how the user usually texts:\n"
            f"{style_examples}\n\n"
            f"{feedback_examples}"
            "Latest incoming message(s) to respond to:\n"
            f"{latest_message}"
        ),
    }


def format_conversation_history(conversation_history: list[dict[str, str]]) -> str:
    if not conversation_history:
        return "No prior messages available."

    lines: list[str] = []
    for message in conversation_history:
        role = "You" if message.get("role") == "user" else "Them"
        text = " ".join(str(message.get("text", "")).split())
        if text:
            lines.append(f"{role}: {text}")
    return "\n".join(lines) if lines else "No prior messages available."


def format_style_examples(conversation_history: list[dict[str, str]]) -> str:
    user_messages = [
        " ".join(str(message.get("text", "")).split())
        for message in conversation_history
        if message.get("role") == "user" and str(message.get("text", "")).strip()
    ]
    if not user_messages:
        return "No recent user examples available."

    examples = user_messages[-5:]
    return "\n".join(f"- {example}" for example in examples)


def infer_preferred_language(
    conversation_history: list[dict[str, str]],
    incoming_messages: list[str],
    language_mix: list[str],
) -> str:
    combined_text = " ".join(
        [message.get("text", "") for message in conversation_history] + incoming_messages
    ).lower()

    if re.search(r"[\u0900-\u097F]", combined_text):
        return "Hindi"

    hindi_marker_count = sum(1 for word in re.findall(r"\b[\w']+\b", combined_text) if word in HINDI_ROMAN_MARKERS)
    english_marker_count = sum(1 for word in re.findall(r"\b[a-z]+\b", combined_text) if len(word) > 2)

    if "Hindi" in language_mix and english_marker_count:
        return "Hinglish"
    if hindi_marker_count >= 3 and english_marker_count >= 6:
        return "Hinglish"
    if hindi_marker_count >= 3:
        return "Hindi"
    return "English"


def describe_reply_length(avg_message_length: float | None) -> str:
    if avg_message_length is None:
        return "short, casual chat length"
    if avg_message_length <= 4:
        return "very short, quick-text style"
    if avg_message_length <= 9:
        return "short, casual chat length"
    return "slightly fuller but still chat-like"





def build_chat_tone_hint(chat_tone_profile: dict, global_tone_profile: dict | None = None) -> str:
    """Build a natural language hint about chat-specific tone differences."""
    hints = []

    if chat_tone_profile.get("formality_score"):
        formality = chat_tone_profile["formality_score"]
        if formality > 4.0:
            hints.append("very formal")
        elif formality > 3.5:
            hints.append("formal")
        elif formality < 2.0:
            hints.append("very casual")
        elif formality < 2.5:
            hints.append("casual")

    if chat_tone_profile.get("punctuation_style"):
        hints.append(f"{chat_tone_profile['punctuation_style']} punctuation style")

    if chat_tone_profile.get("common_emojis"):
        emoji_list = chat_tone_profile["common_emojis"][:2]
        hints.append(f"often uses emojis like: {' '.join(emoji_list)}")

    if chat_tone_profile.get("message_openers"):
        openers = chat_tone_profile["message_openers"][:2]
        hints.append(f"often starts messages with: {', '.join(openers)}")

    return " | ".join(hints) if hints else ""
