from pydantic import BaseModel, Field


class TrainToneRequest(BaseModel):
    samples: list[str] = Field(min_length=1)


class TrainFromMessagesRequest(BaseModel):
    messages: list[str] = Field(min_length=1)
    source: str = Field(default="whatsapp", description="Source of messages (whatsapp, telegram, sms, etc)")


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


class TrainingStatsResponse(BaseModel):
    total_samples_trained: int
    whatsapp_samples: int
    manual_samples: int
    last_training_time: str | None
    accuracy_score: float
    most_common_slang: list[str]
