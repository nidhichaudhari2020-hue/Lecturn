import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
CHROMA_DB_PATH = "data/chroma_db"
COLLECTION_NAME = "study_notes"

# LLM Model
LLM_MODEL = "llama-3.3-70b-versatile"