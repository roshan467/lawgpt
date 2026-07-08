"""
main.py — FastAPI backend exposing the LawGPT RAG pipeline as a REST API.
Run: uvicorn main:app --reload --port 8010
"""
from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import answer_question
from llm_interface import is_ollama_available

app = FastAPI(title="LawGPT", version="1.0.0",
              description="RAG-based legal information assistant (Ollama-powered)")


class Question(BaseModel):
    question: str
    top_k: int = 3


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LawGPT",
        "ollama_available": is_ollama_available(),
    }


@app.post("/api/v1/ask")
def ask(payload: Question):
    return answer_question(payload.question, top_k=payload.top_k)


@app.get("/api/v1/knowledge-base")
def knowledge_base_info():
    from retriever import Retriever
    r = Retriever()
    sources = sorted(set(d["source"] for d in r.documents))
    return {"documents": sources, "total_chunks": len(r.documents)}
