import streamlit as st
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@st.cache_resource(show_spinner=False)
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def generate_embeddings(texts):
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