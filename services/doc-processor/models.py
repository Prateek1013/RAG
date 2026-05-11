from pydantic import BaseModel
from typing import List
from datetime import datetime

class QueryRequest(BaseModel):
    file_id: str
    user_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    
class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
