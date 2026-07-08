"""
app.py — LawGPT Streamlit chat interface.
Run: streamlit run frontend/app.py
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from rag_pipeline import answer_question
from llm_interface import is_ollama_available

st.set_page_config(page_title="LawGPT", page_icon="⚖️", layout="centered")

st.title("⚖️ LawGPT — Legal Information Assistant")
st.caption("RAG-powered legal Q&A — retrieval works offline, generation uses a local Ollama model")

ollama_status = is_ollama_available()
if ollama_status:
    st.success("🟢 LIVE mode — connected to local Ollama model")
else:
    st.warning("🟡 EXTRACTIVE mode — Ollama not detected. Run `ollama serve` + `ollama pull llama3` for full generated answers.")

st.info("⚠️ This is a demo knowledge base covering Indian consumer, tenant, and employment law basics for educational purposes only. It is **not** a substitute for advice from a qualified lawyer.")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a legal question (e.g. 'Can my landlord evict me without notice?')")

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant legal context..."):
            result = answer_question(question)
        st.markdown(result["answer"])
        with st.expander(f"📄 Retrieved context ({result['mode']})"):
            for chunk in result["retrieved_chunks"]:
                st.markdown(f"**{chunk['source']}** (relevance: {chunk['score']})")
                st.text(chunk["text"])
    st.session_state.history.append({"role": "assistant", "content": result["answer"]})
