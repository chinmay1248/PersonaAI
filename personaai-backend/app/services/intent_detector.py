"""Intent detection service for classifying message purpose.

Classifies the sender's intent using pattern and heuristic matching
so the AI engine can produce more relevant reply suggestions.
No LLM needed — runs offline and fast.
"""

import re
from dataclasses import dataclass


@dataclass
class DetectedIntent:
    """Result of intent detection."""
    primary: str
    confidence: float
    secondary: str | None = None

    def label(self) -> str:
        """Human-readable label for prompt inclusion."""
        descriptions = {
            "question": "asking a question or seeking information",
            "plan": "making or discussing a plan",
            "affection": "showing affection or flirting",
            "banter": "casual banter, teasing, or joking around",
            "complaint": "sharing a problem, frustration, or complaint",
            "sharing": "sharing an update, news, opinion, or experience",
            "confirmation": "confirming something or acknowledging",
            "request": "requesting an action or favour",
        }
        return descriptions.get(self.primary, "sharing an update and expecting a natural reaction")


class IntentDetectorService:
    """Detects the likely intent behind one or more incoming messages."""

    # ── Pattern sets ──────────────────────────────────────────────

    QUESTION_PATTERNS = [
        r"\?",
        r"\b(what|where|when|who|how|why|which|whose|whom)\b",
        r"\b(kya|kab|kaha|kaise|kyun|kidhar|kaun|kitna|kitne|kitni)\b",
        r"\b(bata|batao|batana|bol|bolo)\b",
        r"\b(is it|are you|do you|did you|can you|will you|would you)\b",
        r"\b(tell me|let me know)\b",
    ]

    PLAN_PATTERNS = [
        r"\b(plan|meet|come|going|let's|lets|wanna go|want to go)\b",
        r"\b(chalein|chalo|milte|milna|aaja|aao|chalte)\b",
        r"\b(time|place|venue|location|where to|what time)\b",
        r"\b(\d{1,2}\s*(?:am|pm|o'clock))\b",
        r"\b(tomorrow|tonight|weekend)\b",
    ]

    AFFECTION_PATTERNS = [
        r"\b(miss you|love you|i love|i miss|luv u|luv you|ily|ly)\b",
        r"\b(baby|babe|jaan|jaanu|darling|sweetheart|cutie|cutu|baccha)\b",
        r"\b(hug|kiss|cuddle|sweet|adorable|beautiful|gorgeous|handsome)\b",
        r"[😘😍🥰❤️💕💖💗💓💞💝♥️🫶]+",
    ]

    BANTER_PATTERNS = [
        r"\b(lol|lmao|rofl|haha|hehe|lolol|bruh|bro come on)\b",
        r"\b(wild|scene|pagal|paagal|mad|crazy|wtf|omg|dude)\b",
        r"\b(savage|burn|oof|rip|dead|ded|lmfao)\b",
        r"(😂|🤣|💀|😭|🤡|🔥|😆){2,}",
    ]

    COMPLAINT_PATTERNS = [
        r"\b(problem|issue|stuck|broken|annoying|frustrated|angry|upset|sad|tired|stressed)\b",
        r"\b(tension|dikkat|pareshan|mushkil|problem|galat|wrong)\b",
        r"\b(sorry|late|delay|cancel|forgot|mistake|mess)\b",
        r"\b(hate|worst|terrible|horrible|awful|pathetic|useless)\b",
        r"\b(can't believe|not fair|so annoying|pissed|irritated)\b",
    ]

    CONFIRMATION_PATTERNS = [
        r"^(ok|okay|k|done|sure|yep|yup|yes|yeah|haan|ha|acha|accha|theek|thik|sahi|cool|alright|fine|gotcha|got it|acha theek|accha thik)\s*[.!]?\s*$",
        r"^(👍|✅|🤝|💯|✔️)\s*$",
        r"\b(noted|understood|will do|on it|roger|bet)\b",
    ]

    REQUEST_PATTERNS = [
        r"\b(please|send|share|forward|give|pass|show|check|bhej|dikhao|de|dena|kar|karo|karna)\b",
        r"\b(can you|could you|would you|will you|mind if|help me|do me a favor)\b",
        r"\b(need|want|require)\s+(you to|your|a|the|some)\b",
    ]

    # ── Core API ──────────────────────────────────────────────────

    @classmethod
    def detect(cls, messages: list[str], conversation_history: list[dict[str, str]] | None = None) -> DetectedIntent:
        """Detect intent from one or more incoming messages.

        Args:
            messages: The incoming message(s) to classify.
            conversation_history: Optional recent conversation for extra context.

        Returns:
            DetectedIntent with primary intent, confidence, and optional secondary.
        """
        combined = " ".join(messages).strip()
        if not combined:
            return DetectedIntent(primary="sharing", confidence=0.3)

        recent_context = ""
        if conversation_history:
            recent_context = " ".join(
                msg.get("text", "") for msg in conversation_history[-5:]
            ).lower()

        scores = cls._score_all(combined, recent_context)

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_intent, best_score = ranked[0]
        second_intent, second_score = ranked[1] if len(ranked) > 1 else (None, 0.0)

        # Normalize confidence to 0.0–1.0
        total = sum(s for _, s in ranked) or 1.0
        confidence = min(1.0, best_score / total + 0.2) if best_score > 0 else 0.3

        return DetectedIntent(
            primary=best_intent,
            confidence=round(confidence, 2),
            secondary=second_intent if second_score > 0 else None,
        )

    # ── Scoring engine ────────────────────────────────────────────

    @classmethod
    def _score_all(cls, text: str, context: str) -> dict[str, float]:
        """Score each intent category against the text."""
        lowered = text.lower()
        combined = f"{context} {lowered}"

        scores: dict[str, float] = {
            "question": cls._match_count(lowered, cls.QUESTION_PATTERNS) * 1.5,
            "plan": cls._match_count(combined, cls.PLAN_PATTERNS) * 1.3,
            "affection": cls._match_count(combined, cls.AFFECTION_PATTERNS) * 1.4,
            "banter": cls._match_count(combined, cls.BANTER_PATTERNS) * 1.2,
            "complaint": cls._match_count(combined, cls.COMPLAINT_PATTERNS) * 1.3,
            "confirmation": cls._match_count(lowered, cls.CONFIRMATION_PATTERNS) * 1.1,
            "request": cls._match_count(combined, cls.REQUEST_PATTERNS) * 1.2,
            "sharing": 0.5,  # baseline fallback
        }

        # Boost question if the latest message ends with "?"
        if text.rstrip().endswith("?"):
            scores["question"] += 2.0

        # Short one-word confirmations are almost certainly confirmations
        word_count = len(text.split())
        if word_count <= 2 and scores["confirmation"] > 0:
            scores["confirmation"] += 5.0

        return scores

    @staticmethod
    def _match_count(text: str, patterns: list[str]) -> float:
        """Count how many patterns match in the text."""
        count = 0.0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
