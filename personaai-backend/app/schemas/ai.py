from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    text: str


class GenerateReplyRequest(BaseModel):
    chat_config_id: str
    incoming_messages: list[str] = Field(min_length=1)
    conversation_history: list[ConversationMessage] = Field(default_factory=list)
    count: int = Field(default=5, ge=1, le=5)


class ReplySuggestionItem(BaseModel):
    id: str
    rank: int
    text: str


class GenerateReplyResponse(BaseModel):
    conversation_id: str
    detected_mood: str
    suggestions: list[ReplySuggestionItem]


class SummarizeRequest(BaseModel):
    messages: list[str] = Field(min_length=1)


class SummarizeResponse(BaseModel):
    summary: str
    action_items: list[str]
