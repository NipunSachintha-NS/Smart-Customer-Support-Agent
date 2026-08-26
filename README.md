# 🛒 Autonomous Customer Support AI Agent

An intelligent, context-aware **Customer Support AI Agent** built using **Python**, **LangChain / LangGraph**, and **OpenAI (GPT-4o-mini)**. 

This agent handles order tracking, business logic enforcement (e.g., conditional order cancellation), and multi-turn customer conversations using persistent in-memory session checkpointing.

---

## 🌟 Key Features

* **🧠 Multi-Turn Conversational Memory:** Implements `MemorySaver` checkpointing to retain context across dialogue turns (e.g., remembering order IDs referenced earlier).
* **⚙️ Custom Tool Execution:** Equipped with custom Python tools (`@tool`) to interface with backend databases and order management systems.
* **🛡️ Autonomous Business Logic:** Dynamically checks real-world constraints (e.g., automatically preventing the cancellation of already shipped orders).
* **💬 Natural Language Understanding:** Powered by `gpt-4o-mini` to deliver professional, context-grounded customer assistance.

---

## 🛠️ Tech Stack

* **Language:** Python 
* **LLM Engine:** OpenAI `gpt-4o-mini`
* **Agent Framework:** LangGraph / LangChain
* **State & Memory Management:** LangGraph Checkpoint (`MemorySaver`)

---

<img width="1133" height="360" alt="image" src="https://github.com/user-attachments/assets/96869d8b-ea2f-43b8-83cc-4c59be8f4feb" />
