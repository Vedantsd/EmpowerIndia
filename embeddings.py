import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings

load_dotenv()

embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HF_API"),
    repo_id="sentence-transformers/all-MiniLM-L6-v2"
)

def embed_text(text: str):
    return FAISS.from_texts(text, embedding=embeddings)