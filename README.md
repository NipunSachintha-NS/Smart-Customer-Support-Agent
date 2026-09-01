# 🤖 Autonomous AI Customer Support Agent 

An enterprise-grade, production-ready AI Customer Support Agent built with **FastAPI**, **LangGraph (ReAct Framework)**, **OpenAI (GPT-4o-mini)**, **SQLAlchemy (SQLite)**, **ChromaDB (RAG)**, and **React + Vite + Tailwind CSS**.

The system handles real-time order tracking, dynamic database updates, support ticket escalation, knowledge base semantic search, guardrail security filters and real-time token streaming with low-latency execution.

---

## 🌟 Key Features

* **⚡ Real-Time Token Streaming (SSE):** FastAPI SSE (`text/event-stream`) integration with token-by-token decoding and typing effects on the frontend.
* **🧠 ReAct Agent Architecture (LangGraph):** Autonomous tool-calling workflow with conversation state checkpointer memory.
* **💾 Persistent Database Layer (SQLAlchemy + SQLite):** Live database CRUD operations for querying orders, mutating order statuses (e.g., cancellations), and logging customer support tickets.
* **📚 RAG Knowledge Base (ChromaDB Vector Store):** Semantic search for company policies, return rules, and warranty guidelines using OpenAI embeddings (`text-embedding-3-small`).
* **🛡️ Security & Guardrails Layer:** Regex-based PII redaction (Credit Cards, Passwords, Emails) and prompt injection/jailbreak defense.
* **🐳 Dockerized Architecture:** Multi-stage production container setup for backend services.
* **🎨 Modern UI/UX:** Responsive dark mode interface with typing indicators, auto-scrolling, and session resets.

---

## 🏗️ Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Axios, Lucide React
- **Backend**: FastAPI, Uvicorn, Pydantic, Python-dotenv
- **AI / Agentic Framework**: LangGraph, LangChain-OpenAI
- **Vector DB / RAG** : ChromaDB, OpenAI Embeddings 
- **Database & ORM** : SQLite, SQLAlchemy |
- **Observability** : LangSmith Tracing v2 |
- **DevOps** : Docker, Docker Volumes |



<img width="842" height="747" alt="image" src="https://github.com/user-attachments/assets/4850831b-2600-4f60-a04e-70f58aefea26" />
<img width="840" height="737" alt="image" src="https://github.com/user-attachments/assets/862ec5b7-90cf-4f7a-90e8-99a27a246079" />
<img width="857" height="737" alt="image" src="https://github.com/user-attachments/assets/89cc0c80-9e5a-48f4-9865-6754501edf22" />


