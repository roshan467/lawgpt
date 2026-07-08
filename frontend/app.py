"""
app.py — LawGPT Streamlit Frontend
"""

import streamlit as st
import requests
import os

st.set_page_config(page_title="LawGPT", page_icon="⚖️", layout="centered")

# Live Backend URL
BACKEND_URL = os.environ.get(
    "LAWGPT_BACKEND_URL",
    "https://lawgpt-ej3d.onrender.com"
)

st.title("⚖️ LawGPT — Legal Information Assistant")
st.caption("RAG-powered Legal Question Answering")

# Backend Health Check
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    response.raise_for_status()
    health = response.json()
    st.success(f"🟢 Backend Status: {health['status']}")
except Exception as e:
    st.error(f"🔴 Backend not reachable.\n\n{e}")
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

        with st.spinner("Searching legal knowledge base..."):

            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/ask",
                    json={
                        "question": question,
                        "top_k": 3
                    },
                    timeout=60
                )

                response.raise_for_status()
                result = response.json()

                st.markdown(result["answer"])

                with st.expander("📄 Retrieved Documents"):
                    for doc in result.get("retrieved_chunks", []):
                        st.markdown(
                            f"**{doc['source']}** (Score: {doc['score']})"
                        )
                        st.write(doc["text"])

                st.session_state.history.append(
                    {
                        "role": "assistant",
                        "content": result["answer"]
                    }
                )

            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e}")

            except Exception as e:
                st.error(f"Unexpected Error: {e}")