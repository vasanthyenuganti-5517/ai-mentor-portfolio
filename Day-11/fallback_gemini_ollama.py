import os
import requests
from google import genai


def call_gemini(prompt: str) -> str:
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def call_ollama(prompt: str) -> str:
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

    try:
        answer = call_gemini(prompt)
        return f"[Gemini]\n{answer}"

    except Exception as e:
        print(f"Gemini failed: {type(e).__name__}: {str(e)[:150]}")

    try:
        answer = call_ollama(prompt)
        return f"[Ollama]\n{answer}"

    except Exception as e:
        return f"ALL FAILED: {type(e).__name__}: {e}"


print("Test 1 — Normal")
print(llm_call("Explain DBMS in one sentence."))

print("\nTest 2 — Force Gemini Failure")
os.environ["GEMINI_API_KEY"] = "wrong"
print(llm_call("Explain stack data structure."))