import requests

def call_llm(prompt):
    url = "http://localhost:1234/v1/chat/completions"

    payload = {
        "model": "google/gemma-3-4b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.0
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    data = response.json()

    return data['choices'][0]['message']['content']