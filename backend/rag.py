from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL

from backend.embedder import generate_embeddings
from backend.vectordb import search_chunks


# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def ask_question(question):
    """
    Answer a user's question using Retrieval-Augmented Generation (RAG).
    """

    # Create embedding for the question
    query_embedding = generate_embeddings([question])[0]

    # Search relevant chunks
    results = search_chunks(query_embedding)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context
    context = ""

    pages = []

    for doc, metadata in zip(documents, metadatas):

        context += f"\nPage {metadata['page']}:\n{doc}\n"

        pages.append(metadata["page"])

    # Prompt
    prompt = f"""
You are Lecturn, an AI Study Assistant.

Answer ONLY using the context below.

If the answer cannot be found in the context, reply exactly:

"I couldn't find the answer in the uploaded study material."

----------------------------

Context:

{context}

----------------------------

Question:

{question}

Answer:
"""

    # Generate response
    response = client.chat.completions.create(

        model=LLM_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )

    answer = response.choices[0].message.content

    return {

        "answer": answer,

        "pages": sorted(list(set(pages)))

    }