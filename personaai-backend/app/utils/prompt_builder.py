import re


HINDI_ROMAN_MARKERS = {
    "acha", "achha", "arre", "bhai", "bro", "haan", "han", "hai", "kar", "karo", "karna",
    "kya", "kyu", "kyun", "mat", "nahi", "nahi", "nhi", "pata", "scene", "sahi", "theek",
    "thik", "yaar", "sab", "tu", "tum", "mera", "meri", "apna", "abhi", "kal",
}

PERSONALITY_DESCRIPTIONS = {
    "funny": "playful and teasing, quick one-liners, never corny",
    "serious": "straightforward and calm, no jokes, no filler",
    "romantic": "warm and affectionate, soft, a little flirty",
    "savage": "sharp and cheeky, roast-y but never actually mean",
    "balanced": "natural and easy-going, matches whatever the chat feels like",
}

# Transcript size is deliberately smaller than the history we store: a small chat
# model loses track of the latest message when the window is filled with old lines.
TRANSCRIPT_LIMIT = 20
STYLE_EXAMPLE_LIMIT = 8


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
    negative_examples: list[str] | None = None,
    count: int = 3,
) -> dict[str, str]:
    personality = (personality_mode or "balanced").lower()
    personality_hint = PERSONALITY_DESCRIPTIONS.get(personality, PERSONALITY_DESCRIPTIONS["balanced"])
    recent_history = conversation_history[-50:]
    latest_messages = [" ".join(str(text).split()) for text in incoming_messages if str(text).strip()]
    latest_message = "\n".join(latest_messages) or "(no message text)"

    language = infer_preferred_language(recent_history, incoming_messages, language_mix or [])
    language_rule = describe_language_rule(language, recent_history, incoming_messages)
    length_hint = describe_reply_length(avg_message_length, chat_tone_profile)
    emoji_rule = describe_emoji_style(common_emojis, chat_tone_profile)
    slang_hint = ", ".join(slang_patterns[:8]) if slang_patterns else "no distinctive slang recorded yet"
    chat_tone_hint = build_chat_tone_hint(chat_tone_profile or {}, global_tone_profile)
    sender_intent = detected_intent or "sharing an update and expecting a natural reaction"

    transcript = format_conversation_history(recent_history, exclude_trailing=latest_messages)
    style_examples = format_style_examples(recent_history)

    system_lines = [
        "You are the user's texting ghostwriter. You write the next message the user will send "
        "in their private chat. The user copies your reply and sends it as-is, so it has to read "
        "exactly like something they typed themselves.",
        "",
        "# CONTEXT",
        f"- Reply language: {language_rule}",
        f"- Reply length: {length_hint}",
        f"- Personality mode: {personality} - {personality_hint}",
        f"- Their latest message sounds: {detected_mood}",
        f"- What they are doing: {sender_intent}",
        f"- Words and slang this user actually uses: {slang_hint}",
        f"- Emoji: {emoji_rule}",
    ]
    if chat_tone_hint:
        system_lines.append(f"- How this specific chat feels: {chat_tone_hint}")

    system_lines += [
        "",
        "# HOW TO WRITE EACH REPLY",
        "1. You are answering ONE message: the latest message shown at the end of the conversation. "
        "Everything above it is background for understanding it, not something to reply to. Never "
        "bring up an older topic unless the latest message brings it up itself.",
        "2. Find the specific thing in that message: the question, the plan, the person, "
        "the item, the joke, or the feeling.",
        "3. Respond to that exact thing. Answer the question if they asked one. React to the actual "
        "item if they showed one. Take their side if they are venting. Play along if they are joking. "
        "Give a real answer if they are making a plan.",
        "4. Treat everything earlier in the conversation as already known. Do not restate it, do not "
        "summarise it, and do not repeat their words back to them.",
        "5. Type it the way this user types: same language, same length, same lowercase or caps habit, "
        "same punctuation, same slang.",
        f"6. Make the {count} options genuinely different choices, not rewordings of one another - for "
        "example one direct reply, one playful reply, and one that asks something back. All of them "
        "must still fit this exact moment in the chat.",
        "",
        "# NEVER",
        "- Never use assistant filler: \"Sure!\", \"Sounds good\", \"That's great\", \"I'd be happy to\", "
        "\"Let me know\", \"Give me a minute\", \"Haha okay\" - unless that is genuinely the exact right reply here.",
        "- Never be vague when they showed, sent, or shared something specific.",
        "- Never explain the reply, add notes, or mention the chat history, the analysis, or that you are an AI.",
        "- Never sound formal, polished, or like customer support in a casual chat.",
        "- Never invent facts, names, plans, or promises that are not in the conversation.",
        "- Never guess someone's gender. If the chat has not made it clear, say they or them, or just "
        "avoid the pronoun.",
        "- Never write a paragraph. One short message per option, the way people actually text.",
        "",
        "# WHAT ROUGH VS GOOD LOOKS LIKE",
        "Them: \"just got the black pyjamas i ordered\"",
        "Rough - rejected: \"That's great! Sounds good.\"  (vague, bot-like, ignores the actual thing)",
        "Good - accepted: \"the black ones? send a pic\"  (reacts to the exact thing, reads like a real text)",
        "That example only shows the difference in quality. Never reuse its words or its topic.",
        "",
        "# OUTPUT",
        f"Write exactly {count} lines. One reply per line. No numbering, no bullets, no quotes, no labels, "
        "no blank lines, and nothing before or after the replies.",
    ]

    user_lines = [
        "CONVERSATION SO FAR (oldest first - \"Me\" is the user you are writing as, \"Them\" is the other person)",
        transcript,
        "",
        "HOW THE USER TEXTS - copy this voice",
        style_examples,
    ]

    if positive_examples:
        user_lines += [
            "",
            "REPLIES THE USER LIKED BEFORE - match this feel",
            "\n".join(f"- {example}" for example in positive_examples[:5]),
        ]

    if negative_examples:
        user_lines += [
            "",
            "REPLIES THE USER REJECTED - avoid this feel",
            "\n".join(f"- {example}" for example in negative_examples[:5]),
        ]

    user_lines += [
        "",
        "THEIR LATEST MESSAGE - this is what you are replying to",
        latest_message,
        "",
        f"Now write exactly {count} replies from Me, one per line, in {language_rule}, {length_hint}.",
    ]

    return {
        "system": "\n".join(system_lines),
        "user": "\n".join(user_lines),
    }


def format_conversation_history(
    conversation_history: list[dict[str, str]],
    exclude_trailing: list[str] | None = None,
    limit: int = TRANSCRIPT_LIMIT,
) -> str:
    if not conversation_history:
        return "No prior messages available. Reply to the latest message on its own."

    lines: list[str] = []
    for message in conversation_history:
        role = "Me" if message.get("role") == "user" else "Them"
        text = " ".join(str(message.get("text", "")).split())
        if text:
            lines.append(f"{role}: {text}")

    # The latest incoming message is shown separately below the transcript, so drop it
    # from the tail here instead of showing the model the same text twice.
    pending = [" ".join(str(text).split()).lower() for text in (exclude_trailing or [])]
    while lines and pending and lines[-1].lower() == f"them: {pending[-1]}":
        lines.pop()
        pending.pop()

    if not lines:
        return "No prior messages available. Reply to the latest message on its own."
    return "\n".join(lines[-limit:])


def format_style_examples(
    conversation_history: list[dict[str, str]],
    limit: int = STYLE_EXAMPLE_LIMIT,
) -> str:
    user_messages = [
        " ".join(str(message.get("text", "")).split())
        for message in conversation_history
        if message.get("role") == "user" and str(message.get("text", "")).strip()
    ]
    if not user_messages:
        return "No examples of the user's own messages yet. Keep the reply short, plain, and casual."

    return "\n".join(f"- {example}" for example in user_messages[-limit:])


def infer_preferred_language(
    conversation_history: list[dict[str, str]],
    incoming_messages: list[str],
    language_mix: list[str],
) -> str:
    combined_text = " ".join(
        [message.get("text", "") for message in conversation_history] + incoming_messages
    ).lower()

    if re.search(r"[ऀ-ॿ]", combined_text):
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


def describe_language_rule(
    language: str,
    conversation_history: list[dict[str, str]],
    incoming_messages: list[str],
) -> str:
    """Spell out the language AND the script, so a Hinglish chat never gets Devanagari back."""
    if language == "English":
        return "English"

    combined_text = " ".join(
        [message.get("text", "") for message in conversation_history] + list(incoming_messages)
    )
    uses_devanagari = bool(re.search(r"[ऀ-ॿ]", combined_text))

    if language == "Hindi":
        if uses_devanagari:
            return "Hindi in Devanagari script, the same script this chat uses"
        return "Hindi written in English letters (Roman script), never Devanagari"

    return "Hinglish - Hindi words written in English letters, mixed with English, never Devanagari"


def describe_reply_length(
    avg_message_length: float | None = None,
    chat_tone_profile: dict | None = None,
) -> str:
    """Turn the learned average word count into an explicit range the model can obey."""
    chat_average = (chat_tone_profile or {}).get("avg_message_length")
    average = chat_average if chat_average else avg_message_length

    if not average:
        return "3 to 12 words, short casual chat length"
    if average <= 4:
        return "2 to 6 words, very short quick-text style"
    if average <= 9:
        return "3 to 10 words, short casual chat length"
    return "8 to 20 words, fuller but still a chat message"


def describe_emoji_style(
    common_emojis: list[str] | None = None,
    chat_tone_profile: dict | None = None,
) -> str:
    emojis = (chat_tone_profile or {}).get("common_emojis") or common_emojis or []
    if not emojis:
        return "this user rarely uses emoji, so do not add any"
    return f"only these, and at most one per reply: {' '.join(emojis[:3])}"


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
        hints.append(f"{chat_tone_profile['punctuation_style']} punctuation")

    if chat_tone_profile.get("caps_usage"):
        hints.append(f"{chat_tone_profile['caps_usage']} capitalisation")

    if chat_tone_profile.get("message_openers"):
        openers = chat_tone_profile["message_openers"][:2]
        hints.append(f"often opens with: {', '.join(openers)}")

    return " | ".join(hints) if hints else ""
