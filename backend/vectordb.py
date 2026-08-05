import chromadb
from config import CHROMA_DB_PATH, COLLECTION_NAME

# Create a persistent ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Create or load the collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


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
                "page": chunk["page"]
            }
        )

    collection.add(
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

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def reset_database():
    """
    Delete all stored notes.
    """

    global collection

    client.delete_collection(COLLECTION_NAME)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    print("Database reset successfully.")