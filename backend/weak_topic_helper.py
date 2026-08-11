from groq import Groq

from config import (
    GROQ_API_KEY,
    LLM_MODEL
)


def generate_weak_topic_solution(topic, mistakes):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    prompt = f"""
You are an expert teacher and personal study tutor.

A student is struggling with this topic:

Topic: {topic}
Number of mistakes: {mistakes}

Do NOT only give advice on how to improve.

Instead, directly teach the student the topic.

Create a practical learning solution using this structure:

## Why This Topic May Be Difficult
Explain the most common confusion related to this topic.

## Quick Explanation
Explain the topic in simple student-friendly language.

## Key Points To Remember
Give 3 to 5 important points.

## Worked Example
Give one clear example and solve it step by step.

## Practice Question
Give one question for the student to try.

## Correct Answer
Give the correct answer.

## Why This Answer Is Correct
Briefly explain the reasoning.

## Memory Trick
Give one simple memory trick or shortcut.

Keep the response concise but useful.

Do not include unrelated information.
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