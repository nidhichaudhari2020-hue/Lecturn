from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL
from backend.embedder import generate_embeddings
from backend.vectordb import search_chunks


def ask_question(question):

    query_embedding = generate_embeddings([question])[0]

    results = search_chunks(query_embedding)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""
    pages = []

    for document, metadata in zip(
        documents,
        metadatas
    ):
        context += (
            f"\nPage {metadata['page']}:\n"
            f"{document}\n"
        )

        pages.append(metadata["page"])

    prompt = f"""
You are Lecturn, an AI Study Assistant.

Answer ONLY using the context below.

If the answer cannot be found in the context, say:

"I couldn't find the answer in the uploaded study material."

Context:

{context}

Question:

{question}

Answer:
"""

    # Create client only when actually needed
    client = Groq(
        api_key=GROQ_API_KEY
    )

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

    answer = (
        response
        .choices[0]
        .message
        .content
    )

    return {
        "answer": answer,
        "pages": sorted(
            list(set(pages))
        )
    }