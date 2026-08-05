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


def generate_quiz():

    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collection = chroma_client.get_collection(COLLECTION_NAME)

    docs = collection.get()["documents"]

    context = "\n\n".join(docs[:30])

    prompt = f"""
You are an expert teacher.

Generate EXACTLY 10 multiple choice questions.

Return ONLY valid JSON.

Format:

[
 {{
   "question":"...",
   "options":[
      "...",
      "...",
      "...",
      "..."
   ],
   "answer":0,
   "topic":"..."
 }}
]

Rules:

- Exactly 10 questions
- Exactly 4 options
- answer is option index (0-3)
- No explanations
- No markdown
- No text outside JSON

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

    text = response.choices[0].message.content

    try:
        return json.loads(text)

    except Exception:
        return []