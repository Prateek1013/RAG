import os
import uuid
from minio import Minio
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from config import MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
from database import SessionLocal, DocumentChunk, FileModel

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
    db = SessionLocal()
    try:
        # Set status to PROCESSING
        file_record = db.query(FileModel).filter(FileModel.id == uuid.UUID(file_id)).first()
        if file_record:
            file_record.file_status = "PROCESSING"
            db.commit()
    except Exception as e:
        print(f"Could not update status to PROCESSING: {e}")
        db.rollback()
    finally:
        db.close()

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
        if not chunks:
            print(f"Warning: No text could be extracted from file {file_id}. The PDF might be scanned or empty.")
            # Set to FAILED since no chunks
            db = SessionLocal()
            try:
                file_record = db.query(FileModel).filter(FileModel.id == uuid.UUID(file_id)).first()
                if file_record:
                    file_record.file_status = "FAILED"
                    db.commit()
            finally:
                db.close()
            return

        db = SessionLocal()
        for chunk in chunks:
            text = chunk.page_content
            # Skip empty chunks
            if not text.strip():
                continue
                
            embedding = model.encode(text).tolist()

            doc_chunk = DocumentChunk(
                file_id=uuid.UUID(file_id),
                user_id=uuid.UUID(user_id),
                content=text,
                embedding=embedding
            )
            db.add(doc_chunk)
        
        # Update file status to SUCCESS
        file_record = db.query(FileModel).filter(FileModel.id == uuid.UUID(file_id)).first()
        if file_record:
            file_record.file_status = "SUCCESS"
            db.commit()
        db.close()
        print(f"Successfully processed and stored {len(chunks)} chunks for file {file_id}")
        
    except Exception as e:
        print(f"Error processing file {file_id}: {e}")
        # Update file status to FAILED
        db = SessionLocal()
        try:
            file_record = db.query(FileModel).filter(FileModel.id == uuid.UUID(file_id)).first()
            if file_record:
                file_record.file_status = "FAILED"
                db.commit()
        except Exception as inner_e:
            db.rollback()
        finally:
            db.close()
    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
