import chromadb
from groq import Groq

from config import (
    GROQ_API_KEY,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    LLM_MODEL,
)

client = Groq(api_key=GROQ_API_KEY)


def generate_summary():

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collection = chroma_client.get_collection(COLLECTION_NAME)

    docs = collection.get()["documents"]

    context = "\n\n".join(docs[:30])

    prompt = f"""
You are an expert teacher.

Using ONLY the study notes below, generate:

# Chapter Summary

## Key Concepts

## Important Definitions

## Important Formulae

## Exam Tips

Keep the summary concise and easy to revise.

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