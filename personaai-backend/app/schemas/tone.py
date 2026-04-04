from pydantic import BaseModel, Field


class TrainToneRequest(BaseModel):
    samples: list[str] = Field(min_length=1)


class ToneProfileResponse(BaseModel):
    profile_id: str
    formality_score: float
    avg_message_length: float
    emoji_frequency: float
    common_emojis: list[str]
    slang_patterns: list[str]
    detected_language_mix: list[str]
    accuracy_score: float
    status: str
