from pydantic import BaseModel


class Message(BaseModel):
    sender: str  # "user" or "assistant"
    text: str


class ChatRequest(BaseModel):
    role: str = "student"
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str
