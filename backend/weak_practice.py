import json
from groq import Groq

from config import (
    GROQ_API_KEY,
    LLM_MODEL
)


def generate_topic_practice(topic):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    prompt = f"""
You are an expert teacher.

Create exactly 3 multiple choice questions
to help a student practice this topic:

Topic: {topic}

Return ONLY valid JSON.

Format:

[
  {{
    "question": "...",
    "options": [
      "...",
      "...",
      "...",
      "..."
    ],
    "answer": 0
  }}
]

Rules:

- Exactly 3 questions
- Exactly 4 options per question
- "answer" must be an integer from 0 to 3
- Questions should begin easy and become slightly harder
- Focus only on the topic provided
- No markdown
- No explanations outside JSON
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

    text = (
        response.choices[0].message.content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return []