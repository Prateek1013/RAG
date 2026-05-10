import os
import uuid
from minio import Minio
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
from database import SessionLocal, DocumentChunk

# Initialize MinIO Client
minio_client = Minio(
    MINIO_URL.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Initialize Embedding Model
model = SentenceTransformer('all-MiniLM-L6-v2')

def process_file(file_id: str, file_path: str, user_id: str):
    local_file_path = f"/tmp/{file_id}.pdf"
    try:
        # 1. Download file from MinIO
        minio_client.fget_object(MINIO_BUCKET, file_path, local_file_path)

        # 2. Extract text and chunk
        loader = PyPDFLoader(local_file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        # 3. Generate embeddings and save to DB
        db = SessionLocal()
        for chunk in chunks:
            text = chunk.page_content
            embedding = model.encode(text).tolist()

            doc_chunk = DocumentChunk(
                file_id=uuid.UUID(file_id),
                user_id=uuid.UUID(user_id),
                content=text,
                embedding=embedding
            )
            db.add(doc_chunk)
        
        db.commit()
        db.close()
        print(f"Successfully processed and stored chunks for file {file_id}")
        
    except Exception as e:
        print(f"Error processing file {file_id}: {e}")
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
