"""
app.py — LawGPT Streamlit Frontend
"""

import streamlit as st
import requests
import os

st.set_page_config(page_title="LawGPT", page_icon="⚖️", layout="centered")

BACKEND_URL = os.environ.get(
    "LAWGPT_BACKEND_URL",
    "https://lawgpt-p2cd.onrender.com"
)

st.title("⚖️ LawGPT — Legal Information Assistant")
st.caption("RAG-powered Legal Question Answering")

# Health Check
try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=10).json()
    st.success(f"🟢 Backend: {health['status']}")
except Exception:
    st.error("🔴 Backend not reachable.")
    st.stop()

st.info(
    "⚠️ Educational demo only. This is not legal advice."
)

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask your legal question...")

if question:

    st.session_state.history.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching..."):

            response = requests.post(
                f"{BACKEND_URL}/api/v1/ask",
                json={
                    "question": question,
                    "top_k": 3
                },
                timeout=60
            )

            result = response.json()

        st.markdown(result["answer"])

        with st.expander("Retrieved Documents"):
            for doc in result["retrieved_chunks"]:
                st.markdown(f"**{doc['source']}**")
                st.write(doc["text"])

    st.session_state.history.append(
        {
            "role": "assistant",
            "content": result["answer"]
        }
    )