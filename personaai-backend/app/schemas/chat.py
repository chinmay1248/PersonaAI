from pydantic import BaseModel, Field


class ChatConfigCreateRequest(BaseModel):
    chat_label: str = Field(min_length=1, max_length=100)
    chat_type: str | None = None
    personality_mode: str | None = None
    auto_reply_mode: str = "OFF"
    ai_enabled: bool = True
    is_private: bool = False


class ChatConfigUpdateRequest(BaseModel):
    chat_label: str | None = Field(default=None, min_length=1, max_length=100)
    chat_type: str | None = None
    personality_mode: str | None = None
    auto_reply_mode: str | None = None
    ai_enabled: bool | None = None
    is_private: bool | None = None


class ChatConfigResponse(BaseModel):
    id: str
    chat_label: str
    chat_type: str | None
    personality_mode: str | None
    auto_reply_mode: str
    ai_enabled: bool
    is_private: bool
