from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Languages, ChatSessionParticipant, ChatSessionStatus
from app.schemas.base import TranslatableModel


class ChatMessageTranslationCreate(BaseModel):
    messages: str
    language: Languages


class ChatMessageCreate(BaseModel):
    session_id: int
    message: str


class ChatMessageDelete(BaseModel):
    pass


class ChatTopic(TranslatableModel):
    id: int
    title: str
    description: str | None

    class Config:
        orm_mode = True


class ChatSession(BaseModel):
    id: int
    status: ChatSessionStatus
    topic: ChatTopic | None = None
    has_new_message: bool = False
    last_message_from: ChatSessionParticipant | None = None
    is_problem_resolved: bool | None = None
    created_at: datetime

    class Config:
        orm_mode = True


class ChatMessage(BaseModel):
    id: int
    message: str
    from_whom: ChatSessionParticipant
    is_seen: bool = False
    is_deleted: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


class ChatSessionMessageList(BaseModel):
    session: ChatSession
    messages: list[ChatMessage]


class ChatSessionCreate(BaseModel):
    topic_id: int


class ChatSessionClose(BaseModel):
    is_problem_resolved: bool = False
