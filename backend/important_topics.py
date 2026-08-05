import chromadb
from groq import Groq
from config import (
    GROQ_API_KEY,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    LLM_MODEL,
)

client = Groq(api_key=GROQ_API_KEY)


def generate_important_topics():

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collection = chroma_client.get_collection(COLLECTION_NAME)

    docs = collection.get()["documents"]

    context = "\n\n".join(docs[:30])

    prompt = f"""
Using ONLY these study notes, list the 10 most important exam topics.

Return the result in Markdown like:

# Important Topics

1.
2.
3.

Study Notes:

{context}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content