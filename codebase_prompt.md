# LawGPT Codebase Prompt

The following is the complete source code for the LawGPT project, an AI Legal Assistant built with Next.js, React, FastAPI, and local LLMs using Ollama.

Please use this codebase as context for my requests.

---

## `app.py`
```python
import streamlit as st
import requests

st.set_page_config(page_title="LawGPT", layout="wide")

st.title("⚖️ LawGPT - AI Legal Assistant")

# Check backend connection
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=2)
    if response.status_code == 200:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Error")
except:
    st.error("❌ Backend Not Running - Run: python rag.py")

# Chat interface
st.subheader("💬 Ask Questions")

for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if prompt := st.chat_input("Ask a legal question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/ask",
                    json={"query": prompt}
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer")
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
            except:
                st.error("Backend not running!")
```

---

## `backend/main.py`
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ✅ ONLY use Ollama-based function
from backend.rag import get_answer, process_file

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request model
class QueryRequest(BaseModel):
    query: str

# 🏠 Home
@app.get("/")
def home():
    return {"message": "⚖️ LawGPT Backend Running 🚀"}

# 📂 Upload (simple processing)
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        result = process_file(file)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# 🤖 Ask (ONLY Ollama — NO OpenAI)
@app.post("/ask")
def ask(data: QueryRequest):
    try:
        print("🔥 Query:", data.query)
        answer = get_answer(data.query)
        print("✅ Answer:", answer)
        return {"answer": answer}
    except Exception as e:
        print("❌ ERROR:", e)
        return {"answer": f"Error: {str(e)}"}
```

---

## `backend/api.py`
```python
from fastapi import FastAPI, UploadFile, File
import shutil
import os

from loader import load_pdf
from vectorstore import create_vectorstore
from rag import get_qa_chain

app = FastAPI()

vectorstore = None
qa_chain = None

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vectorstore, qa_chain

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = load_pdf(file_path)
    vectorstore = create_vectorstore(docs)
    qa_chain = get_qa_chain(vectorstore)

    return {"message": "File processed successfully"}


@app.get("/ask")
def ask(query: str):
    global qa_chain

    if qa_chain is None:
        return {"answer": "Please upload a file first."}

    result = qa_chain.run(query)
    return {"answer": result}
```

---

## `backend/rag.py`
```python
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

def get_qa_chain(vectorstore):
    llm = Ollama(model="llama3")  # make sure ollama pull llama3

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever()
    )
    return qa
```

---

## `backend/vectorstore.py`
```python
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

def create_vectorstore(docs):
    embedding = OllamaEmbeddings(model="llama3")

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory="backend/vectorstore"
    )
    return vectorstore
```

---

## `backend/loader.py`
```python
from langchain.document_loaders import PyPDFLoader

def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs
```

---

## `client/package.json`
```json
{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "@ai-sdk/groq": "^3.0.35",
    "@ai-sdk/react": "^3.0.158",
    "ai": "^6.0.156",
    "lucide-react": "^1.8.0",
    "next": "16.2.3",
    "react": "19.2.4",
    "react-dom": "19.2.4",
    "react-markdown": "^10.1.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "eslint": "^9",
    "eslint-config-next": "16.2.3",
    "tailwindcss": "^4"
  }
}
```

---

## `client/src/app/api/chat/route.js`
```javascript
import { streamText } from 'ai';
import { createGroq } from '@ai-sdk/groq';

const groq = createGroq({
  apiKey: process.env.GROQ_API_KEY
});

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req) {
  try {
    const { messages, data } = await req.json();

    const result = streamText({
      model: groq('llama-3.3-70b-versatile'),
      system: 'You are LawGPT, a highly knowledgeable and professional AI legal assistant specializing in Indian Law. You help users understand their legal rights and analyze their situations. Always add a disclaimer that you are an AI and this is not formal legal advice.',
      messages,
    });

    return result.toDataStreamResponse();
  } catch (error) {
    console.error("Chat API Error:", error);
    return new Response(JSON.stringify({ error: "Failed to process chat request." }), { status: 500 });
  }
}
```

---

## `client/src/app/layout.js`
```javascript
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
```

---

## `client/src/app/page.js`
```javascript
"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '@ai-sdk/react';
import { Bot, User, Paperclip, Send, Plus, MessageSquare, X, Scale } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const clearFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    if (!(input || '').trim() && !file) return;
    
    // Custom submit to handle file if needed
    handleSubmit(e, {
      data: file ? { fileName: file.name, fileType: file.type } : undefined
    });
    
    setFile(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <div className="layout">
      {/* Sidebar */}
      <div className="sidebar">
        <button className="new-chat-btn" onClick={() => window.location.reload()}>
          <Plus size={18} />
          <span>New Chat</span>
        </button>
        
        <div className="history-list">
          <div className="history-item">
            <MessageSquare size={14} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
            Landlord Eviction Notice
          </div>
          <div className="history-item">
            <MessageSquare size={14} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
            Starting an LLC in India
          </div>
          <div className="history-item">
            <MessageSquare size={14} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
            Intellectual Property Rights
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Scale size={48} color="#20a16c" style={{ marginBottom: '16px' }} />
              <h1>LawGPT</h1>
              <p>Your AI Legal Assistant. Ask questions, upload legal documents, and get instant guidance.</p>
            </div>
          ) : (
            messages.map((m) => (
              <div key={m.id} className={`message-wrapper ${m.role === 'user' ? 'user-wrapper' : 'bot-wrapper'}`}>
                <div className={`message ${m.role}`}>
                  <div className={`avatar ${m.role}`}>
                    {m.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </div>
                  <div className="message-content">
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && messages[messages.length - 1]?.role === 'user' && (
            <div className="message-wrapper py-4">
              <div className="message bot">
                <div className="avatar bot"><Bot size={18} /></div>
                <div className="message-content">
                  <span className="animate-pulse">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <div className="input-box">
              {file && (
                <div className="file-pill">
                  <Paperclip size={14} />
                  <span>{file.name}</span>
                  <button onClick={clearFile} type="button">
                    <X size={14} />
                  </button>
                </div>
              )}
              
              <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                <textarea
                  className="text-input"
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask a legal question..."
                  rows={Math.min(Math.max((input || '').split('\n').length, 1), 6)}
                />
                
                <div className="input-actions">
                  <button type="button" className="icon-btn" onClick={() => fileInputRef.current?.click()}>
                    <Paperclip size={18} />
                  </button>
                  <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileChange}
                    accept=".pdf,.txt,.doc,.docx"
                  />
                  
                  <button 
                    type="submit" 
                    className="send-btn" 
                    disabled={!(input || '').trim() && !file || isLoading}
                  >
                    <Send size={16} />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## `client/src/app/globals.css`
```css
:root {
  --bg-color: #0f1115;
  --sidebar-bg: #16181d;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --accent-color: #3f68e0;
  --input-bg: #1e2128;
  --border-color: #2a2d36;
  --user-msg-bg: transparent;
  --bot-msg-bg: transparent;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-color);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.layout {
  display: flex;
  width: 100vw;
  height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--sidebar-bg);
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 16px;
  border-right: 1px solid var(--border-color);
  transition: transform 0.3s ease;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  margin-bottom: 24px;
  justify-content: flex-start;
}

.new-chat-btn:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.history-list {
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
  background: none;
  border: none;
}

.history-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

/* Main Content */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
}

/* Chat Area */
.chat-area {
  flex-grow: 1;
  overflow-y: auto;
  padding-bottom: 120px;
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chat-area::-webkit-scrollbar {
  width: 8px;
}
.chat-area::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.1);
  border-radius: 4px;
}

.message-wrapper {
  width: 100%;
  padding: 24px 20px;
  display: flex;
  justify-content: center;
}

.message {
  width: 100%;
  max-width: 800px;
  display: flex;
  gap: 16px;
  line-height: 1.6;
}

.avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  color: white;
}

.avatar.user {
  background-color: #eb4d4b;
}

.avatar.bot {
  background-color: #20a16c;
}

.message-content {
  flex-grow: 1;
  color: #ececec;
}

.message-content pre {
  background-color: #0d0f12;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid var(--border-color);
}
.message-content code {
  font-family: monospace;
  background: #1a1c23;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.9em;
}
.message-content pre code {
  background: transparent;
  padding: 0;
}
.message-content p {
  margin-bottom: 12px;
}
.message-content p:last-child {
  margin-bottom: 0;
}

.input-area {
  padding: 20px 0 40px;
  width: 100%;
  display: flex;
  justify-content: center;
  background: linear-gradient(180deg, rgba(15,17,21,0) 0%, rgba(15,17,21,1) 30%);
  position: absolute;
  bottom: 0;
}

.input-container {
  width: 100%;
  max-width: 800px;
  padding: 0 20px;
  position: relative;
}

.input-box {
  display: flex;
  flex-direction: column;
  background-color: var(--input-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-box:focus-within {
  border-color: rgba(255,255,255,0.2);
}

.text-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
  font-size: 16px;
  resize: none;
  font-family: inherit;
  max-height: 200px;
  padding: 0;
  line-height: 1.5;
  width: 100%;
}

.text-input::placeholder {
  color: #666;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  transition: background-color 0.2s, color 0.2s;
}

.icon-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.send-btn {
  background-color: #20a16c;
  color: white;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
}

.send-btn:hover {
  background-color: #1a8f5f;
}

.send-btn:disabled {
  background-color: transparent;
  color: var(--text-secondary);
  cursor: not-allowed;
}

.file-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #2b303b;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 8px;
  border: 1px solid var(--border-color);
}

.file-pill button {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  margin-top: 20vh;
}

.empty-state h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 12px;
  background: linear-gradient(90deg, #20a16c, #3f68e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 16px;
  max-width: 400px;
  margin: 0 auto;
}
```
