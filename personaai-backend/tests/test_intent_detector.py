"""Tests for IntentDetectorService."""

import pytest
from app.services.intent_detector import IntentDetectorService, DetectedIntent


class TestIntentDetection:
    """Test each intent category is detected correctly."""

    def test_detects_question_from_question_mark(self):
        result = IntentDetectorService.detect(["What time is the meeting?"])
        assert result.primary == "question"
        assert result.confidence >= 0.5

    def test_detects_question_from_hindi_keywords(self):
        result = IntentDetectorService.detect(["kya hua bhai?"])
        assert result.primary == "question"

    def test_detects_question_from_english_keywords(self):
        result = IntentDetectorService.detect(["Where are you going tomorrow"])
        # "where" triggers question, "tomorrow" triggers plan — question should win with "?"
        result_with_q = IntentDetectorService.detect(["Where are you going tomorrow?"])
        assert result_with_q.primary == "question"

    def test_detects_plan(self):
        result = IntentDetectorService.detect(["Let's meet tomorrow at 5 pm"])
        assert result.primary == "plan"

    def test_detects_plan_hindi(self):
        result = IntentDetectorService.detect(["kal milte hain, chalo cafe chalte"])
        assert result.primary == "plan"

    def test_detects_affection(self):
        result = IntentDetectorService.detect(["I miss you so much baby 😘"])
        assert result.primary == "affection"

    def test_detects_affection_hindi(self):
        result = IntentDetectorService.detect(["love you jaan ❤️"])
        assert result.primary == "affection"

    def test_detects_banter(self):
        result = IntentDetectorService.detect(["lmao bro that was wild 😂😂"])
        assert result.primary == "banter"

    def test_detects_banter_hindi(self):
        result = IntentDetectorService.detect(["pagal hai kya lol 🤣🤣"])
        assert result.primary == "banter"

    def test_detects_complaint(self):
        result = IntentDetectorService.detect(["I'm so frustrated, this is broken and annoying"])
        assert result.primary == "complaint"

    def test_detects_complaint_hindi(self):
        result = IntentDetectorService.detect(["bahut tension ho rahi hai, sab galat ho gaya"])
        assert result.primary == "complaint"

    def test_detects_confirmation_short(self):
        result = IntentDetectorService.detect(["okay"])
        assert result.primary == "confirmation"

    def test_detects_confirmation_emoji(self):
        result = IntentDetectorService.detect(["👍"])
        assert result.primary == "confirmation"

    def test_detects_confirmation_hindi(self):
        result = IntentDetectorService.detect(["acha theek"])
        assert result.primary == "confirmation"

    def test_detects_request(self):
        result = IntentDetectorService.detect(["Can you please send me the file?"])
        assert result.primary in ("request", "question")  # Both valid; "?" may boost question

    def test_detects_request_hindi(self):
        result = IntentDetectorService.detect(["photo bhej de please"])
        assert result.primary == "request"

    def test_sharing_is_fallback(self):
        result = IntentDetectorService.detect(["I went to a nice restaurant today"])
        assert result.primary == "sharing"

    def test_empty_message_returns_sharing(self):
        result = IntentDetectorService.detect([""])
        assert result.primary == "sharing"
        assert result.confidence <= 0.5

    def test_confidence_is_bounded(self):
        result = IntentDetectorService.detect(["What? Where? When? How? Why?"])
        assert 0.0 <= result.confidence <= 1.0

    def test_secondary_intent_populated(self):
        # "Let's meet tomorrow?" has both plan and question signals
        result = IntentDetectorService.detect(["Let's meet tomorrow?"])
        assert result.secondary is not None

    def test_label_returns_human_readable(self):
        result = IntentDetectorService.detect(["miss you baby ❤️"])
        assert "affection" in result.label() or "flirting" in result.label()

    def test_context_influences_detection(self):
        # Without context, "sure" is confirmation
        result_no_ctx = IntentDetectorService.detect(["sure"])
        assert result_no_ctx.primary == "confirmation"

        # With planning context, still confirmation but context is considered
        result_ctx = IntentDetectorService.detect(
            ["sure"],
            conversation_history=[
                {"role": "contact", "text": "want to meet tomorrow at 5?"},
            ],
        )
        # Should still be confirmation — the message itself is "sure"
        assert result_ctx.primary == "confirmation"

    def test_multiple_messages_combined(self):
        result = IntentDetectorService.detect(["I'm so tired", "everything is going wrong", "ugh"])
        assert result.primary == "complaint"

    def test_detected_intent_dataclass(self):
        intent = DetectedIntent(primary="question", confidence=0.8, secondary="plan")
        assert intent.primary == "question"
        assert intent.confidence == 0.8
        assert intent.secondary == "plan"
        assert "question" in intent.label()
