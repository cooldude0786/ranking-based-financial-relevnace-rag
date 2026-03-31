from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# vector DB
client = chromadb.Client(Settings(persist_directory="./chroma_db"))

collection = client.get_or_create_collection(name="documents")