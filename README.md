# 🤖 Autonomous AI Customer Support Agent 

A production-grade, containerized AI Customer Support Agent built with **LangGraph**, **FastAPI**, and **React**. The system leverages ReAct agent patterns, dynamic tool calling with business rule validation, conversational memory checkpoints and session isolation.

---

## 🌟 Key Features

- **Autonomous Tool Calling**: Uses OpenAI models via LangGraph to automatically determine whether to query order statuses or execute cancellations.
- **Business Rule Enforcement**: Built-in validation prevents cancellation of orders that have already shipped.
- **Thread-Level Memory Isolation**: Uses LangGraph's `MemorySaver` to maintain persistent multi-turn conversations scoped strictly to unique `session_id` threads.
- **RESTful Microservice Architecture**: FastAPI backend structured with Pydantic data validation schemas and CORS security.
- **Modern Responsive UI**: Built with React (Vite), Tailwind CSS, and Lucide Icons with real-time feedback and session resets.
- **Dockerized Deployment**: Fully containerized backend service running on lightweight `python:3.11-slim`.

---

## 🏗️ Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Axios, Lucide React
- **Backend**: FastAPI, Uvicorn, Pydantic, Python-dotenv
- **AI / Agentic Framework**: LangGraph, LangChain-OpenAI
- **Containerization**: Docker, Docker Compose



<img width="842" height="747" alt="image" src="https://github.com/user-attachments/assets/4850831b-2600-4f60-a04e-70f58aefea26" />
<img width="840" height="737" alt="image" src="https://github.com/user-attachments/assets/862ec5b7-90cf-4f7a-90e8-99a27a246079" />
<img width="857" height="737" alt="image" src="https://github.com/user-attachments/assets/89cc0c80-9e5a-48f4-9865-6754501edf22" />


