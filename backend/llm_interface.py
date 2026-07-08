"""
llm_interface.py — calls a locally-running Ollama model to generate the
final answer from retrieved legal context. This is the "G" (Generation)
in RAG.

Ollama runs as a local server (https://ollama.com) — it is NOT a pip
package with bundled models, so it cannot be installed or run inside this
sandboxed environment (no internet access to download model weights).
This code is written to call a real, running Ollama instance and will
work immediately on your own machine once you:

    1. Install Ollama:        https://ollama.com/download
    2. Pull a model:          ollama pull llama3
    3. Start the server:      ollama serve   (usually auto-starts)

If Ollama isn't reachable, this falls back to an honest EXTRACTIVE mode —
it returns the most relevant retrieved passage directly instead of a
generated answer, clearly labeled as such. This keeps the system fully
functional and demoable even without Ollama installed.
"""
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"

LEGAL_SYSTEM_PROMPT = """You are LawGPT, a legal information assistant. \
Answer the user's question using ONLY the provided context below. \
If the context doesn't contain enough information, say so clearly. \
Always end your answer with: "This is general legal information, not a \
substitute for advice from a qualified lawyer." """


def is_ollama_available(timeout=1.5) -> bool:
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=timeout)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def generate_answer(question: str, context_chunks: list, model: str = DEFAULT_MODEL) -> dict:
    context_text = "\n\n".join(f"[{c['source']}]: {c['text']}" for c in context_chunks)

    if not context_chunks:
        return {
            "answer": "I couldn't find relevant information in the knowledge base for this question. "
                      "This is general legal information, not a substitute for advice from a qualified lawyer.",
            "mode": "no_context",
        }

    if is_ollama_available():
        prompt = f"{LEGAL_SYSTEM_PROMPT}\n\nContext:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            resp.raise_for_status()
            return {"answer": resp.json()["response"].strip(), "mode": "live_ollama", "model": model}
        except requests.exceptions.RequestException as e:
            return _extractive_fallback(context_chunks, error=str(e))

    return _extractive_fallback(context_chunks)


def _extractive_fallback(context_chunks: list, error: str = None) -> dict:
    """Honest fallback: returns the top retrieved passage directly rather
    than fabricating a generated answer when no LLM is available."""
    best = context_chunks[0]
    answer = (
        f"[Ollama not available — showing most relevant retrieved passage instead]\n\n"
        f"\"{best['text'].strip()}\"\n\n(Source: {best['source']})\n\n"
        f"This is general legal information, not a substitute for advice from a qualified lawyer."
    )
    return {"answer": answer, "mode": "extractive_fallback", "error": error}
