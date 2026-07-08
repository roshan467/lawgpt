"""
ingest.py — loads legal documents, splits them into overlapping chunks
(standard RAG preprocessing step), and builds a TF-IDF retrieval index.

Why TF-IDF instead of neural embeddings: this environment has no internet
access to download embedding models (e.g. sentence-transformers) from
HuggingFace. TF-IDF + cosine similarity is a real, classic information-
retrieval technique that works fully offline and gives solid results for
a small, focused knowledge base like this one. See README for how to
upgrade to neural embeddings once you have internet access.
"""
import os
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "legal_docs")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "index.pkl")

CHUNK_SIZE = 400       # characters per chunk
CHUNK_OVERLAP = 80     # overlap between consecutive chunks


def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def load_documents():
    documents = []  # list of {"text": ..., "source": ...}
    for fname in sorted(os.listdir(DOCS_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for i, chunk in enumerate(chunk_text(text)):
            documents.append({"text": chunk, "source": fname, "chunk_id": i})
    return documents


def build_index():
    documents = load_documents()
    texts = [d["text"] for d in documents]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    matrix = vectorizer.fit_transform(texts)

    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "documents": documents}, f)

    return len(documents)


if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks from {len(os.listdir(DOCS_DIR))} documents into {INDEX_PATH}")
