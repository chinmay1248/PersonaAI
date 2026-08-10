from app.utils.prompt_builder import build_reply_prompt, describe_reply_length


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


def test_prompt_includes_style_examples_and_specificity_rules() -> None:
    prompt = _prompt()

    assert "Never be vague when they showed, sent, or shared something specific." in prompt["system"]
    assert "HOW THE USER TEXTS" in prompt["user"]
    assert "- show me properly" in prompt["user"]


def test_prompt_states_output_contract_for_the_requested_count() -> None:
    prompt = _prompt(count=4)

    assert "Write exactly 4 lines. One reply per line." in prompt["system"]
    assert "Now write exactly 4 replies from Me" in prompt["user"]


def test_latest_message_is_not_duplicated_in_the_transcript() -> None:
    prompt = _prompt()

    transcript, _, latest_block = prompt["user"].partition("THEIR LATEST MESSAGE")
    assert "Them: The black pyjamas I got" not in transcript
    assert "The black pyjamas I got" in latest_block
    assert "Me: show me properly" in transcript


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


def test_missing_user_examples_do_not_leave_an_empty_section() -> None:
    prompt = _prompt(conversation_history=[{"role": "contact", "text": "yo"}])

    assert "No examples of the user's own messages yet" in prompt["user"]
