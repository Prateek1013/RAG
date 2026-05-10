from fastapi import FastAPI, HTTPException
from models import QueryRequest, QueryResponse
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
