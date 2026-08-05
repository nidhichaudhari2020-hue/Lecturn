import streamlit as st
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@st.cache_resource(show_spinner=False)
def load_embedding_model():
    """
    Load and cache the embedding model.

    The model is loaded once per running app instance
    instead of being recreated during every Streamlit rerun.
    """
    return SentenceTransformer(EMBEDDING_MODEL)


def generate_embeddings(texts):
    """
    Convert a list of text strings into embedding vectors.
    """
    if not texts:
        return []

    model = load_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings.tolist()