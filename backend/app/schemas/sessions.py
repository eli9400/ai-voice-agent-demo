from pydantic import BaseModel, Field


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str


class MessageRequest(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    session_id: str
    user_message: str
    assistant_message: str
    message_count: int


class SessionMessage(BaseModel):
    user_message: str
    assistant_message: str


class SessionDetailResponse(BaseModel):
    session_id: str
    messages: list[SessionMessage]
