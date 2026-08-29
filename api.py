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
from rag_engine import search_store_knowledge

load_dotenv()

# Initialize DB & Seed Data
init_db()

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
        
        order.status = "Cancelled"
        db.commit()
        return f"Success: Order '{clean_id}' has been marked as Cancelled in the database."
    finally:
        db.close()

@tool
def create_support_ticket(issue_description: str) -> str:
    """Create and persist a support ticket when a customer has a complaint, damaged item, or requires human escalation."""
    db = SessionLocal()
    try:
        ticket = SupportTicket(issue_description=issue_description)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return f"Support ticket #{ticket.id} created successfully for issue: '{issue_description}'."
    except Exception as e:
        return f"Failed to create support ticket: {str(e)}"
    finally:
        db.close()

@tool
def lookup_store_policy(query: str) -> str:
    """Search the TechGear knowledge base for store policies including returns, refunds, warranty periods, and shipping guidelines."""
    return search_store_knowledge(query)

tools = [get_order_status, cancel_order, create_support_ticket,lookup_store_policy]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
memory = MemorySaver()

system_prompt = (
    "You are a professional customer support agent for TechGear Store. "
    "Always identify yourself as TechGear Support. "
    "For inquiries regarding return rules, warranty coverage, or shipping policies, always query the knowledge base tool (lookup_store_policy). "
    "For order queries, use get_order_status or cancel_order. "
    "For severe issues or damaged goods, create a support ticket. Be concise, polite, and precise."
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

@app.get("/tickets")
def get_all_tickets():
    """Retrieve all support tickets from the database."""
    db = SessionLocal()
    try:
        tickets = db.query(SupportTicket).all()
        return [
            {
                "id": t.id,
                "issue_description": t.issue_description,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tickets
        ]
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Support Agent"}