import os

import requests

def call_llm(prompt):
    url = os.getenv(
        "LM_STUDIO_URL",
        "http://localhost:1234/v1/chat/completions"
    )
    model = os.getenv("LLM_MODEL", "google/gemma-3-4b")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0
    }

    response = requests.post(url, json=payload, timeout=120)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    data = response.json()

    return data['choices'][0]['message']['content']
