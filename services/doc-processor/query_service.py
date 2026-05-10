import uuid
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from groq import Groq
from database import SessionLocal, DocumentChunk
from config import GROQ_API_KEY

# Initialize Embedding Model (same as used in processor.py)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Groq Client
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

def process_query(file_id: str, user_id: str, query: str) -> str:
    if not groq_client:
        return "GROQ_API_KEY is not configured. Please add it to the .env file."

    # 1. Embed user query
    query_embedding = model.encode(query).tolist()
    
    # 2. Search Database using PGVector Cosine Distance
    db = SessionLocal()
    try:
        stmt = (
            select(DocumentChunk)
            .filter(DocumentChunk.file_id == uuid.UUID(file_id))
            .filter(DocumentChunk.user_id == uuid.UUID(user_id))
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(5)
        )
        
        results = db.execute(stmt).scalars().all()
        
        if not results:
            return "No relevant information found in the document to answer your query."
            
        # Combine the chunks into a single context string
        context_chunks = [r.content for r in results]
        context_text = "\n\n---\n\n".join(context_chunks)
        
        # 3. Construct Prompt and Call Groq LLM
        prompt = f"""You are an intelligent assistant. Answer the user's question based strictly on the provided context.

Context:
{context_text}

Question:
{query}

Answer the question based ONLY on the context provided. If the context does not contain the answer, say "I cannot answer this based on the provided document."
"""
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.2, # Low temperature for more factual answers
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return f"An error occurred while processing your query: {str(e)}"
    finally:
        db.close()
