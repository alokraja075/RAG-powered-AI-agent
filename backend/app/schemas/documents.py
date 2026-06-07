from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    indexed: bool
    created_at: datetime


class IndexResponse(BaseModel):
    document_id: int
    indexed: bool
