"""
retriever.py — retrieves the top-k most relevant document chunks for a
query using TF-IDF + cosine similarity (the "R" in RAG).
"""
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "index.pkl")


class Retriever:
    def __init__(self, index_path=INDEX_PATH):
        with open(index_path, "rb") as f:
            data = pickle.load(f)
        self.vectorizer = data["vectorizer"]
        self.matrix = data["matrix"]
        self.documents = data["documents"]

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.05):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked_idx = scores.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_idx:
            if scores[idx] < min_score:
                continue
            doc = self.documents[idx]
            results.append({
                "text": doc["text"],
                "source": doc["source"],
                "score": round(float(scores[idx]), 4),
            })
        return results
