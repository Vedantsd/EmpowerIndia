import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embedding, text):
        vec = np.array([embedding]).astype("float32")
        self.index.add(vec)
        self.texts.append(text)

    def search(self, embedding, k=5):
        vec = np.array([embedding]).astype("float32")
        _, indices = self.index.search(vec, k)
        return [self.texts[i] for i in indices[0]]
