from app.utils.prompt_builder import build_reply_prompt, infer_sender_intent


def test_build_reply_prompt_includes_style_examples_and_specificity_rules() -> None:
    prompt = build_reply_prompt(
        incoming_messages=["The black pyjamas I got"],
        conversation_history=[
            {"role": "contact", "text": "which one should I wear?"},
            {"role": "user", "text": "show me properly"},
            {"role": "contact", "text": "The black pyjamas I got"},
            {"role": "user", "text": "hmm not bad actually"},
        ],
        personality_mode="funny",
        detected_mood="neutral",
        slang_patterns=["bro", "yaar"],
        language_mix=["English", "Hindi"],
        avg_message_length=4.5,
        common_emojis=[],
    )

    assert "Avoid generic filler" in prompt["system"]
    assert "Recent examples of how the user usually texts" in prompt["user"]
    assert "- show me properly" in prompt["user"]


def test_infer_sender_intent_detects_item_discussion() -> None:
    intent = infer_sender_intent(
        ["The black pyjamas I got"],
        [{"role": "contact", "text": "which one should I wear?"}],
    )

    assert "item" in intent or "appearance" in intent
