import json
import chromadb
from groq import Groq

from config import (
    GROQ_API_KEY,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    LLM_MODEL,
)


def generate_flashcards():

    # Groq client loads only when flashcards are generated
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

    # Use first 30 chunks
    context = "\n\n".join(docs[:30])

    # Prompt
    prompt = f"""
You are an expert teacher.

Generate exactly 15 flashcards from the study notes below.

Return ONLY valid JSON.

Format:

[
  {{
    "question": "...",
    "answer": "..."
  }}
]

Rules:
- Generate exactly 15 flashcards
- Focus on important concepts
- Keep answers clear and concise
- Use only the supplied study notes
- Do not include markdown
- Do not include text outside JSON

Study Notes:

{context}
"""

    # Generate flashcards
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

    text = response.choices[0].message.content

    # Remove markdown if the AI accidentally adds it
    text = (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Convert JSON text into Python list
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return []