import uuid
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from groq import Groq
from database import SessionLocal, DocumentChunk, ChatMessage
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
        
        # 3. Save User Query to DB
        user_msg = ChatMessage(
            file_id=uuid.UUID(file_id),
            user_id=uuid.UUID(user_id),
            role="user",
            content=query
        )
        db.add(user_msg)
        db.commit()

        # 4. Fetch Chat History
        past_msgs = db.query(ChatMessage).filter(
            ChatMessage.file_id == uuid.UUID(file_id),
            ChatMessage.user_id == uuid.UUID(user_id)
        ).order_by(ChatMessage.created_at.asc()).all()

        # 5. Construct Prompt with History and Call Groq LLM
        system_prompt = f"""You are an intelligent assistant. Answer the user's questions based strictly on the provided document context.

Context:
{context_text}

If the context does not contain the answer, say "I cannot answer this based on the provided document."
"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add historical messages except the last one (which is the current query)
        for msg in past_msgs[:-1]:
            messages.append({"role": msg.role, "content": msg.content})
            
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.2, # Low temperature for more factual answers
        )
        
        answer = chat_completion.choices[0].message.content
        
        # 6. Save Assistant Response to DB
        assistant_msg = ChatMessage(
            file_id=uuid.UUID(file_id),
            user_id=uuid.UUID(user_id),
            role="assistant",
            content=answer
        )
        db.add(assistant_msg)
        db.commit()
        
        return answer
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return f"An error occurred while processing your query: {str(e)}"
    finally:
        db.close()
