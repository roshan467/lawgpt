"""
rag_pipeline.py — ties retrieval and generation together into a single
question-answering pipeline.
"""

from backend.retriever import Retriever
from backend.llm_interface import generate_answer, is_ollama_available

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def answer_question(question: str, top_k: int = 3) -> dict:
    retriever = get_retriever()
    chunks = retriever.retrieve(question, top_k=top_k)

    result = generate_answer(question, chunks)

    result["retrieved_chunks"] = chunks
    result["ollama_available"] = is_ollama_available()

    return result