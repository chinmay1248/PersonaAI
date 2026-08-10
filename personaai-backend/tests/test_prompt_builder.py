from app.utils.prompt_builder import (
    build_reply_prompt,
    describe_register_rule,
    describe_reply_length,
)


def _prompt(**overrides):
    kwargs = dict(
        incoming_messages=["The black pyjamas I got"],
        conversation_history=[
            {"role": "contact", "text": "which one should I wear?"},
            {"role": "user", "text": "show me properly"},
            {"role": "contact", "text": "The black pyjamas I got"},
        ],
        personality_mode="funny",
        detected_mood="neutral",
        slang_patterns=["bro", "yaar"],
        language_mix=["English", "Hindi"],
        avg_message_length=4.5,
        common_emojis=[],
        detected_intent="showing or discussing an item, look, or appearance",
        count=3,
    )
    kwargs.update(overrides)
    return build_reply_prompt(**kwargs)


def test_prompt_states_the_specificity_rules() -> None:
    prompt = _prompt()

    assert "Never be vague when they showed, sent, or shared something specific." in prompt["system"]


def test_prompt_states_output_contract_for_the_requested_count() -> None:
    prompt = _prompt(count=4)

    assert "Write exactly 4 lines. One reply per line." in prompt["system"]
    assert "Now write exactly 4 replies to that message" in prompt["user"]


def test_no_earlier_message_reaches_the_model() -> None:
    """Only the message being answered may appear in the prompt."""
    prompt = _prompt()
    whole_prompt = prompt["system"] + prompt["user"]

    assert "The black pyjamas I got" in prompt["user"]
    for earlier in ("which one should I wear?", "show me properly"):
        assert earlier not in whole_prompt

    # And the model is told it has no history rather than left to imagine one.
    assert "not shown anything that was said before it" in prompt["system"]
    assert "Never refer to an earlier message" in prompt["system"]


def test_history_still_drives_language_detection_without_being_shown() -> None:
    hinglish = _prompt(
        incoming_messages=["ok"],
        conversation_history=[
            {"role": "contact", "text": "bhai kal ka kya scene hai"},
            {"role": "user", "text": "haan yaar dekhte hain"},
        ],
        language_mix=[],
    )

    assert "Hinglish" in hinglish["system"]
    assert "scene hai" not in hinglish["system"] + hinglish["user"]


def test_hinglish_chat_is_told_to_avoid_devanagari() -> None:
    prompt = _prompt(
        incoming_messages=["kal milna hai kya"],
        conversation_history=[
            {"role": "contact", "text": "bro kal ka kya scene hai"},
            {"role": "user", "text": "haan yaar dekhte hain"},
        ],
    )

    assert "Hinglish" in prompt["system"]
    assert "never Devanagari" in prompt["system"]


def test_devanagari_chat_keeps_its_script() -> None:
    prompt = _prompt(
        incoming_messages=["कल मिलना है क्या"],
        conversation_history=[{"role": "contact", "text": "कल का क्या प्लान है"}],
        language_mix=["Hindi"],
    )

    assert "Devanagari script" in prompt["system"]
    assert "never Devanagari" not in prompt["system"]


def test_emoji_rule_suppresses_emoji_when_the_user_never_uses_them() -> None:
    assert "do not add any" in _prompt(common_emojis=[])["system"]
    assert "😂" in _prompt(common_emojis=["😂", "🔥"])["system"]


def test_chat_tone_profile_length_overrides_the_global_average() -> None:
    assert describe_reply_length(20.0) == "8 to 20 words, fuller but still a chat message"
    assert describe_reply_length(20.0, {"avg_message_length": 3.0}).startswith("2 to 6 words")


def test_disliked_replies_are_shown_as_an_anti_example() -> None:
    prompt = _prompt(negative_examples=["Sounds good, let me know!"])

    assert "REPLIES THE USER REJECTED" in prompt["user"]
    assert "- Sounds good, let me know!" in prompt["user"]


def test_hindi_register_comes_from_the_learned_formality_score() -> None:
    """Without a transcript, tu/tum vs aap has to come from the tone profile."""
    assert "never aap" in describe_register_rule("Hinglish", {"formality_score": 2.0})
    assert "use aap" in describe_register_rule("Hinglish", {"formality_score": 4.2})
    assert "never aap" in describe_register_rule("Hindi", None)
    assert describe_register_rule("English", {"formality_score": 4.2}) == ""


def test_casual_hinglish_prompt_rules_out_aap() -> None:
    prompt = _prompt(
        incoming_messages=["kal milna hai kya"],
        conversation_history=[{"role": "contact", "text": "bro kal ka kya scene hai"}],
        chat_tone_profile={"formality_score": 2.0},
    )

    assert "Politeness register: informal - use tu or tum, never aap" in prompt["system"]


def test_liked_replies_are_marked_as_style_only() -> None:
    prompt = _prompt(positive_examples=["haan bilkul, kitne baje?"])

    assert "match their feel, never their subject" in prompt["user"]
    assert "- haan bilkul, kitne baje?" in prompt["user"]
