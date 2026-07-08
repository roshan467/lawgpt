# LawGPT — RAG-Powered Legal Information Assistant

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

## How to run

```bash
pip install -r requirements.txt

# 1. Build the retrieval index
python backend/ingest.py

# 2. (Optional, for full generated answers) Install Ollama and pull a model:
#    https://ollama.com/download
ollama pull llama3
ollama serve   # usually starts automatically after install

# 3. Run the API
cd backend && uvicorn main:app --reload --port 8010

# 4. Run the chat frontend (separate terminal)
streamlit run frontend/app.py
```

## Important honesty notes (read before your interview)

1. **This sandbox couldn't run Ollama** (no internet access to download model weights), so every test I ran here used the honest **extractive fallback** mode — verified working, retrieval correctly finds the right document every time. **You must run this with Ollama on your own machine at least once** before discussing "generated answers" in an interview.

2. **The knowledge base is a small demo set** (3 topics: consumer, tenant, employment law basics) that I wrote — not scraped from a real legal database or bar association source. Be upfront about this: *"I built a RAG pipeline with a demo legal knowledge base to prove out the architecture — production use would need a licensed legal content source."*

3. **This is not legal advice software** — every answer includes a disclaimer, and this should never be positioned as a replacement for consulting an actual lawyer. Say this explicitly if asked about real-world deployment.

4. **Embeddings are TF-IDF, not neural**, because this environment has no internet access to download sentence-transformer models. TF-IDF is a legitimate, classic IR technique that works well for a small, focused knowledge base — but for a production system, upgrading to neural embeddings (`sentence-transformers`, e.g. `all-MiniLM-L6-v2`) would improve semantic matching on paraphrased questions. This is a natural, honest "future work" talking point.

## Tech stack
Python · scikit-learn (TF-IDF, cosine similarity) · FastAPI · Ollama · Streamlit
