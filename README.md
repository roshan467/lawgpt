# LawGPT — RAG-Powered Legal Information Assistant  -  https://bit.ly/4vmC3Vl

A Retrieval-Augmented Generation (RAG) system that answers legal questions by retrieving relevant passages from a legal knowledge base and generating a grounded answer using a locally-run LLM via **Ollama**.

## Architecture (real RAG, not a wrapper around an API)

```
User Question
     │
     ▼
┌─────────────┐     TF-IDF + Cosine Similarity
│  Retriever   │ ──► Top-k relevant passages from knowledge base
└─────────────┘
     │
     ▼
┌─────────────┐     Context + Question → Prompt
│ LLM Interface│ ──► Ollama (local model) generates grounded answer
└─────────────┘     Falls back to extractive mode if Ollama unavailable
     │
     ▼
  Final Answer (with source attribution)
```

## What this demonstrates
- **Real RAG pipeline**: document chunking → TF-IDF vectorization → cosine-similarity retrieval → LLM generation — not just a ChatGPT API wrapper
- **Local LLM integration** via Ollama (no per-query API costs, runs entirely on your machine)
- **Honest degradation**: works even without Ollama running (extractive fallback), clearly labeled — no fake/hallucinated "LIVE" claims
- **Source attribution**: every answer traces back to which document it came from
- Unit-tested retrieval layer (6/6 tests passing)

## Files
```
LawGPT/
├── backend/
│   ├── ingest.py           # chunks legal docs, builds TF-IDF index
│   ├── retriever.py        # cosine-similarity search over the index
│   ├── llm_interface.py    # Ollama integration + honest fallback
│   ├── rag_pipeline.py     # wires retrieval + generation together
│   └── main.py             # FastAPI REST API
├── frontend/
│   └── app.py              # Streamlit chat interface
├── tests/
│   └── test_retriever.py   # 6 tests, all passing
└── data/legal_docs/        # sample knowledge base (consumer/tenant/employment law)
```
```


## Tech stack
Python · scikit-learn (TF-IDF, cosine similarity) · FastAPI · Ollama · Streamlit
