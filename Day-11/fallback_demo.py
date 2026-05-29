import os
import requests
from google import genai
from groq import Groq


def call_gemini(prompt: str) -> str:
    # Call Gemini API.
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def call_groq(prompt: str) -> str:
    # Call Groq API.
    client = Groq(
        api_key=os.environ["GROQ_API_KEY"]
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def call_ollama(prompt: str) -> str:
    # Call local Ollama API.
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    return response.json()["response"]


def llm_call(prompt: str) -> str:
    # Provider fallback chain: Gemini -> Groq -> Ollama

    # 1. Try Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            answer = call_gemini(prompt)
            return f"[Gemini]\n{answer}"

        except Exception as e:
            print(f"Gemini failed: {type(e).__name__}: {str(e)[:150]}")

    # 2. Try Groq
    if os.environ.get("GROQ_API_KEY"):
        try:
            answer = call_groq(prompt)
            return f"[Groq]\n{answer}"

        except Exception as e:
            print(f"Groq failed: {type(e).__name__}: {str(e)[:150]}")

    # 3. Try local Ollama
    try:
        answer = call_ollama(prompt)
        return f"[Ollama]\n{answer}"

    except Exception as e:
        return f"ALL FAILED: {type(e).__name__}: {e}"


if __name__ == "__main__":

    print("\nTest 1 — Normal Path")
    print(llm_call("Explain Big-O notation in one sentence."))

    print("\n" + "=" * 60)

    print("\nTest 2 — Force Gemini Failure")
    os.environ["GEMINI_API_KEY"] = "wrong-key-on-purpose"
    print(llm_call("What is recursion?"))

    print("\n" + "=" * 60)

    print("\nTest 3 — Force Gemini + Groq Failure")
    os.environ["GEMINI_API_KEY"] = "wrong"
    os.environ["GROQ_API_KEY"] = "wrong"
    print(llm_call("Define inheritance in OOP."))