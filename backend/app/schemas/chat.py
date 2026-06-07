from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    top_k: int = 4


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    created_at: str
