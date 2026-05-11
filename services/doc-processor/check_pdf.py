from minio import Minio
from langchain_community.document_loaders import PyPDFLoader
import traceback

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

try:
    minio_client.fget_object("files", "f0997958-a554-4ac0-830d-67697c802631_12th.pdf", "test.pdf")
    loader = PyPDFLoader("test.pdf")
    documents = loader.load()
    print("Number of documents loaded:", len(documents))
    for i, doc in enumerate(documents):
        print(f"Doc {i} length:", len(doc.page_content))
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
