import chromadb
import streamlit as st
from uuid import uuid4
from config import CHROMA_DB_PATH, COLLECTION_NAME

# Create a persistent ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

def _collection_name():
    """Return a private collection name for the current browser session."""
    if "workspace_id" not in st.session_state:
        st.session_state.workspace_id = uuid4().hex
    return f"{COLLECTION_NAME}_{st.session_state.workspace_id}"


def get_collection():
    return client.get_or_create_collection(name=_collection_name())


def get_documents():
    """Return only documents belonging to this session."""
    return get_collection().get().get("documents", [])


def store_chunks(chunks, embeddings):
    """
    Store chunks and embeddings in ChromaDB.
    """

    ids = []

    documents = []

    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(str(index))

        documents.append(chunk["text"])

        metadatas.append(
            {
                "page": chunk["page"],
                "source": chunk.get("source", "Study notes")
            }
        )

    get_collection().add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks successfully.")


def search_chunks(query_embedding, top_k=5):
    """
    Retrieve the most relevant chunks.
    """

    results = get_collection().query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def reset_database():
    """
    Delete all stored notes.
    """

    name = _collection_name()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    client.get_or_create_collection(name=name)

    print("Database reset successfully.")