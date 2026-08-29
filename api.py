import os
import json
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from database import init_db, SessionLocal, Order, SupportTicket

load_dotenv()

# Initialize DB & Seed Data
init_db()

# --- SQLAlchemy Database Tools ---
@tool
def get_order_status(order_id: str) -> str:
    """Fetch real-time order status from the SQL database using the order ID."""
    clean_id = order_id.upper().strip()
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == clean_id).first()
        if not order:
            return f"Order '{clean_id}' was not found in our database."
        return f"Order {order.id} for '{order.item}' is currently {order.status}. Delivery info: {order.delivery_date}."
    finally:
        db.close()

@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order in the SQL database if eligible (must be 'Processing')."""
    clean_id = order_id.upper().strip()
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == clean_id).first()
        if not order:
            return f"Cannot cancel: Order '{clean_id}' not found."
        if order.status == "Shipped":
            return f"Cancellation failed: Order '{clean_id}' has already shipped."
        if order.status == "Delivered":
            return f"Cancellation failed: Order '{clean_id}' was already delivered."
        if order.status == "Cancelled":
            return f"Order '{clean_id}' is already cancelled."
        
        # Persistent Update
        order.status = "Cancelled"
        db.commit()
        return f"Success: Order '{clean_id}' has been marked as Cancelled in the database."
    finally:
        db.close()

@tool
def create_support_ticket(session_id: str, issue_description: str) -> str:
    """Create and persist a support ticket if an issue needs human escalation."""
    db = SessionLocal()
    try:
        ticket = SupportTicket(session_id=session_id, issue_description=issue_description)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return f"Support ticket #{ticket.id} created successfully for issue: '{issue_description}'."
    finally:
        db.close()

# --- Agent Configuration ---
tools = [get_order_status, cancel_order, create_support_ticket]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
memory = MemorySaver()

system_prompt = (
    "You are a helpful customer support agent for TechGear Store. "
    "Always identify yourself as TechGear Support. Use your database tools to query orders, "
    "cancel processing orders, and file support tickets for user complaints. Strictly enforce policies."
)

agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    prompt=system_prompt,
)

app = FastAPI(title="Customer Support AI Agent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

async def generate_chat_stream(message: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    try:
        async for event in agent_executor.astream_events(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            version="v2"
        ):
            kind = event.get("event")
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    payload = json.dumps({"chunk": chunk.content})
                    yield f"data: {payload}\n\n"
                    await asyncio.sleep(0.04)
    except Exception as e:
        err_payload = json.dumps({"chunk": f" [Server Error: {str(e)}] "})
        yield f"data: {err_payload}\n\n"
        
    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        generate_chat_stream(request.message, request.session_id),
        media_type="text/event-stream"
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Support Agent with Persistent DB"}