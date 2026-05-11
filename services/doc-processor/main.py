from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from models import QueryRequest, QueryResponse, ChatHistoryResponse, ChatMessageResponse
from kafka_consumer import KafkaConsumerThread
from query_service import process_query

app = FastAPI(title="Doc Processor Service")

consumer_thread = None

@app.on_event("startup")
def startup_event():
    global consumer_thread
    consumer_thread = KafkaConsumerThread()
    consumer_thread.start()

@app.on_event("shutdown")
def shutdown_event():
    global consumer_thread
    if consumer_thread:
        consumer_thread.stop()
        consumer_thread.join()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest):
    try:
        answer = process_query(request.file_id, request.user_id, request.query)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history/{file_id}", response_model=ChatHistoryResponse)
def get_chat_history(file_id: str, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    from database import SessionLocal, ChatMessage
    import uuid
    db = SessionLocal()
    try:
        msgs = db.query(ChatMessage).filter(
            ChatMessage.file_id == uuid.UUID(file_id),
            ChatMessage.user_id == uuid.UUID(x_user_id)
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return ChatHistoryResponse(
            messages=[
                ChatMessageResponse(
                    id=str(m.id),
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at
                ) for m in msgs
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
