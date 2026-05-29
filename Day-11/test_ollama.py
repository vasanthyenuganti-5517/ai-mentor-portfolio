import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": "Explain OOP in simple words.",
        "stream": False
    },
    timeout=60
)

print(response.json()["response"])