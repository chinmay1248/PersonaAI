"""Tests for feedback-driven reply ranking."""

import pytest
from app.services.ai_engine import AIEngineService


class TestFeedbackRanking:
    def test_rerank_replies_promotes_positive_patterns(self):
        replies = [
            "Sure, I can do that",
            "Absolutely!",
            "I guess so",
        ]
        positive_patterns = ["absolutely sure", "can do"]
        negative_patterns = []

        ranked = AIEngineService._rerank_replies(replies, positive_patterns, negative_patterns)
        
        # 'Absolutely!' has "absolutely"
        # 'Sure, I can do that' has "sure"
        # Since 'absolutely sure' gives points for 'absolutely' and 'sure', let's see which gets more.
        # "Absolutely!" (1 point)
        # "Sure, I can do that" (1 point for 'sure')
        # Actually both get some points, but let's test a clear winner.
        
        replies_2 = ["Okay", "That is fantastic news"]
        pos_2 = ["fantastic news"]
        ranked_2 = AIEngineService._rerank_replies(replies_2, pos_2, [])
        assert ranked_2[0] == "That is fantastic news"

    def test_rerank_replies_demotes_negative_patterns(self):
        replies = [
            "I am sorry to hear that",
            "Okay, fine",
            "Whatever you say",
        ]
        positive_patterns = []
        negative_patterns = ["whatever fine"]

        ranked = AIEngineService._rerank_replies(replies, positive_patterns, negative_patterns)
        
        # 'Whatever you say' gets -1
        # 'Okay, fine' gets -1
        # 'I am sorry to hear that' gets 0 -> should be first
        assert ranked[0] == "I am sorry to hear that"

    def test_rerank_replies_handles_empty_patterns(self):
        replies = ["A", "B", "C"]
        ranked = AIEngineService._rerank_replies(replies, [], [])
        assert ranked == replies

    def test_rerank_replies_combined_patterns(self):
        replies = [
            "I absolutely love this",
            "This is terrible",
            "Okay",
        ]
        positive_patterns = ["absolutely love"]
        negative_patterns = ["terrible"]

        ranked = AIEngineService._rerank_replies(replies, positive_patterns, negative_patterns)
        assert ranked[0] == "I absolutely love this"
        assert ranked[1] == "Okay"
        assert ranked[2] == "This is terrible"
