import os
import requests

HF_API = os.getenv("HF_API")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {
    "Authorization": f"Bearer {HF_API}"
}

def embed_text(text: str):
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": text}
    )
    response.raise_for_status()
    embedding = response.json()
    return embedding
