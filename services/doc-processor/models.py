from pydantic import BaseModel

class QueryRequest(BaseModel):
    file_id: str
    user_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str
