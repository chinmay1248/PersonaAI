from pydantic import BaseModel


class ReplyFeedbackRequest(BaseModel):
    reply_suggestion_id: str
    rating: str
    reason: str | None = None


class ReplyFeedbackResponse(BaseModel):
    status: str
    message: str
