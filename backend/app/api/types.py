from pydantic import BaseModel
from typing import Optional, Any


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class ChatSendRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatMessage(BaseModel):
    message_id: str
    role: str
    content: str
    agent_id: Optional[str] = None
    card_type: Optional[str] = None


class IntentParseRequest(BaseModel):
    session_id: str
    message: str


class Entities(BaseModel):
    departure: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    headcount: Optional[int] = None
    user_level: Optional[str] = None
    purpose: Optional[str] = None


class Question(BaseModel):
    field: str
    question: str
    options: Optional[list[str]] = None


class IntentData(BaseModel):
    intent_type: str
    entities: Entities
    missing_fields: list[str]
    questions: list[Question]


class ClarifyRequest(BaseModel):
    session_id: str
    answers: dict[str, str]
