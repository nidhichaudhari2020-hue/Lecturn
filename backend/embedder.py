from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Load the embedding model only once
model = SentenceTransformer(EMBEDDING_MODEL)

def generate_embeddings(texts):
    """
    Generate embeddings for a list of text chunks.
    Returns a list of vectors.
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()