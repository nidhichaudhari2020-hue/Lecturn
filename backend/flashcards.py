import json
import chromadb
from groq import Groq

from config import (
    GROQ_API_KEY,
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    LLM_MODEL,
)

client = Groq(api_key=GROQ_API_KEY)


def generate_flashcards():

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collection = chroma_client.get_collection(COLLECTION_NAME)

    docs = collection.get()["documents"]

    context = "\n\n".join(docs[:30])

    prompt = f"""
You are an expert teacher.

Generate exactly 15 flashcards.

Return ONLY valid JSON.

Format:

[
 {{
   "question":"...",
   "answer":"..."
 }}
]

No markdown.

Study Notes:

{context}
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.3
    )

    text = response.choices[0].message.content

    text = text.replace("```json","").replace("```","").strip()

    try:
        return json.loads(text)
    except:
        return []