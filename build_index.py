from pdf_utils import load_pdf
from chunker import chunk_text
from embeddings import embeddings
from langchain_community.vectorstores import FAISS

print("Loading PDF...")
text = load_pdf("src/constitution.pdf")

chunks = chunk_text(text)

print("Building FAISS index...")
vectorstore = FAISS.from_texts(
    texts=chunks,
    embedding=embeddings
)

vectorstore.save_local("constitutionDB")

print("Index ready.")
