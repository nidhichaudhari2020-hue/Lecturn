import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Local development: .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Streamlit Cloud: Secrets
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = None

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your local .env "
        "or Streamlit Cloud Secrets."
    )

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHROMA_DB_PATH = "data/chroma_db"
COLLECTION_NAME = "study_notes"

LLM_MODEL = "llama-3.3-70b-versatile"