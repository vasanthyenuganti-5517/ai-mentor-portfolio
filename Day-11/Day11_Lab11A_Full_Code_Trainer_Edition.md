# Day 11 — Lab 11A: Ollama Offline + Hybrid Fallback
## Updated Trainer Edition with Full Code

---

## Lab Goal

Build and demonstrate a production-style fallback chain:

```text
Gemini Cloud
↓ if Gemini fails
Groq Cloud
↓ if Groq fails
Ollama Local
```

By the end of the lab, participants will:
- Install Ollama locally
- Download and run a local LLM
- Test AI without internet
- Build Gemini → Groq → Ollama fallback chain
- Force cloud failures and verify local fallback
- Record Wi-Fi disconnect demo
- Push code and README to GitHub

---

# Part 1 — Environment Check

Run these commands in **Windows PowerShell**.

```powershell
py --version
```

Expected:

```text
Python 3.10 or higher
```

Check pip:

```powershell
py -m pip --version
```

Install required Python packages:

```powershell
py -m pip install groq google-genai requests
```

Verify packages:

```powershell
py -m pip list
```

---

# Part 2 — Install Ollama

Download and install Ollama for Windows:

```text
https://ollama.com/download/windows
```

After installation, close and reopen PowerShell.

Verify:

```powershell
ollama --version
```

Expected:

```text
ollama version x.x.x
```

---

# Part 3 — Pull Local Model

For standard laptops:

```powershell
ollama pull llama3.2
```

For low RAM laptops:

```powershell
ollama pull phi3:mini
```

Check downloaded models:

```powershell
ollama list
```

Expected:

```text
NAME        ID        SIZE
llama3.2    ...       ...
```

---

# Part 4 — Test Ollama in Terminal

Run:

```powershell
ollama run llama3.2
```

Ask:

```text
What is recursion in computer science?
```

Important:

```text
First response may take 30–60 seconds.
This is normal because the model is loading into RAM.
```

---

# Part 5 — Wi-Fi Disconnect Demo

1. Keep Ollama running.
2. Disconnect Wi-Fi.
3. Ask:

```text
What is object-oriented programming?
```

Expected:

```text
Ollama still answers.
```

Teaching line:

```text
The laptop itself becomes the AI server.
```

---

# Part 6 — Test Ollama API Directly

Create a file named:

```text
test_ollama.py
```

Add this code:

```python
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
```

Run:

```powershell
py test_ollama.py
```

Expected:

```text
Ollama returns answer through local API.
```

If error comes:

```text
Connection refused localhost:11434
```

Run:

```powershell
ollama serve
```

Then retry.

---

# Part 7 — Set API Keys

In PowerShell:

```powershell
$env:GEMINI_API_KEY="PASTE_YOUR_GEMINI_KEY"
$env:GROQ_API_KEY="PASTE_YOUR_GROQ_KEY"
```

Verify:

```powershell
echo $env:GEMINI_API_KEY
echo $env:GROQ_API_KEY
```

---

# Part 8 — Create Full Fallback Demo File

Create a Python file:

```text
fallback_demo.py
```

Paste this full code:

```python
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
```

Run:

```powershell
py fallback_demo.py
```

---

# Part 9 — Expected Outputs

## Test 1

Expected:

```text
[Gemini]
...
```

## Test 2

Expected:

```text
Gemini failed...
[Groq]
...
```

## Test 3

Expected:

```text
Gemini failed...
Groq failed...
[Ollama]
...
```

This proves the fallback chain works.

---

# Part 10 — Ultra-Safe Version Without Groq

Use this if Groq package/API key is not available.

Create:

```text
fallback_gemini_ollama.py
```

Code:

```python
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
```

Run:

```powershell
py fallback_gemini_ollama.py
```

---

# Part 11 — README Content

Add this to README:

```markdown
## Day 11 Lab 11A — Ollama Offline + Hybrid Fallback

### Completed
- ✅ Ollama installed locally
- ✅ llama3.2 model downloaded
- ✅ Offline AI tested after Wi-Fi disconnect
- ✅ Gemini → Groq → Ollama fallback chain implemented
- ✅ Force-failure testing completed
- ✅ Local fallback verified

### Demo Proof
- Wi-Fi disconnect demo recorded
- Fallback chain outputs captured

### Reflection
1. First inference is slow because the model loads into RAM.
2. Ollama is useful for privacy, offline access, and zero per-call cost.
3. Production AI systems should not depend on a single provider.

### Architecture

Gemini Cloud → Groq Cloud → Ollama Local
```

---

# Common Errors and Fixes

## Error: pip not recognized

Use:

```powershell
py -m pip install groq google-genai requests
```

---

## Error: ModuleNotFoundError: groq

Fix:

```powershell
py -m pip install groq
```

---

## Error: ollama not recognized

Fix:
- Restart terminal
- Restart laptop if required
- Reinstall Ollama

---

## Error: localhost:11434 connection refused

Fix:

```powershell
ollama serve
```

---

## Error: first response slow

This is normal.

Reason:

```text
Model is loading into RAM.
```

---

## Error: Groq model not found

Change model name in code:

```python
model="llama-3.1-8b-instant"
```

or use the current model from Groq console.

---

# Teaching Explanation

Say:

```text
Gemini is cloud AI.
Groq is cloud backup.
Ollama is local backup.
```

Then say:

```text
Production AI systems should survive provider failure.
```

Most important classroom line:

```text
AI Engineering is reliability engineering.
```

---

# Acceptance Checklist

- Python works
- pip works using py -m pip
- Ollama installed
- Model downloaded
- Ollama terminal test works
- Ollama API test works
- Gemini test works
- Groq test works
- Fallback chain works
- Wi-Fi disconnect demo recorded
- README updated
- GitHub pushed
