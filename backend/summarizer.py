import chromadb
from groq import Groq

from config import (
    GROQ_API_KEY,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    LLM_MODEL,
)


def generate_summary():

    # Create Groq client only when summary is requested
    client = Groq(api_key=GROQ_API_KEY)

    # Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH
    )

    collection = chroma_client.get_collection(
        COLLECTION_NAME
    )

    # Get indexed notes
    docs = collection.get()["documents"]

    # Use a limited amount of context
    context = "\n\n".join(docs[:30])

    prompt = f"""
You are an expert teacher.

Using ONLY the study notes below, create a concise and
revision-friendly summary.

Use this structure:

# Chapter Summary

## Key Concepts

## Important Definitions

## Important Formulae

## Exam Tips

Rules:
- Use only the supplied study notes
- Keep the explanation easy to understand
- Focus on important exam-relevant information
- Do not invent information that is not present in the notes
- Use clear headings and bullet points where useful

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
        ],
        temperature=0.3
    )

    return response.choices[0].message.content