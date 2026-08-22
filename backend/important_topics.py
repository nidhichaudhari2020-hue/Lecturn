from groq import Groq

from config import (
    GROQ_API_KEY,
    LLM_MODEL,
)
from backend.vectordb import get_documents


def generate_important_topics():

    # Create Groq client only when this feature is used
    client = Groq(api_key=GROQ_API_KEY)

    # Connect to ChromaDB
    docs = get_documents()

    # Limit context size
    context = "\n\n".join(docs[:30])

    prompt = f"""
You are an expert teacher helping a student prepare for exams.

Using ONLY the study notes below, identify the 10 most
important topics that the student should revise.

For each topic:
- Give the topic name
- Give a short reason why it is important
- Keep the explanation concise

Return the result in Markdown using this format:

# Important Topics

1. **Topic Name**
   - Why it is important

2. **Topic Name**
   - Why it is important

Continue until exactly 10 topics are listed.

Rules:
- Use only the supplied study notes
- Do not invent unrelated topics
- Focus on definitions, concepts, algorithms, formulas,
  comparisons, and frequently examinable ideas

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