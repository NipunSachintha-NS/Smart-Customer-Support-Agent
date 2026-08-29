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

load_dotenv()

# --- Mock Database ---
ORDERS_DB: Dict[str, Dict[str, Any]] = {
    "ORD101": {"item": "Wireless Headphones", "status": "Shipped", "delivery_date": "Tomorrow at 2:00 PM"},
    "ORD102": {"item": "Mechanical Keyboard", "status": "Processing", "delivery_date": "Pending"},
    "ORD103": {"item": "USB-C Hub", "status": "Delivered", "delivery_date": "Delivered Yesterday"},
}

@tool
def get_order_status(order_id: str) -> str:
    """Fetch order status using the order ID."""
    clean_id = order_id.upper().strip()
    order = ORDERS_DB.get(clean_id)
    if not order:
        return f"Order '{clean_id}' was not found in our database."
    return f"Order {clean_id} for '{order['item']}' is currently {order['status']}. Delivery info: {order['delivery_date']}."

@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order if eligible (must be 'Processing')."""
    clean_id = order_id.upper().strip()
    order = ORDERS_DB.get(clean_id)
    if not order:
        return f"Cannot cancel: Order '{clean_id}' not found."
    if order["status"] == "Shipped":
        return f"Cancellation failed: Order '{clean_id}' has already shipped."
    if order["status"] == "Delivered":
        return f"Cancellation failed: Order '{clean_id}' was already delivered."
    
    order["status"] = "Cancelled"
    return f"Success: Order '{clean_id}' has been cancelled."

# --- Agent Configuration ---
tools = [get_order_status, cancel_order]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
memory = MemorySaver()

system_prompt = (
    "You are a helpful customer support agent for TechGear Store. "
    "Always identify yourself as TechGear Support. Use your tools to check order statuses "
    "and process cancellations. Be concise, polite, and strictly follow cancellation policies."
)

agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    prompt=system_prompt,
)

# --- FastAPI Initialization ---
app = FastAPI(
    title="Customer Support AI Agent API",
    description="Production REST API for TechGear Customer Support Agent",
    version="1.0.0"
)

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

# --- Streaming Handler with Tuned Delay ---
async def generate_chat_stream(message: str, session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    try:
        async for event in agent_executor.astream_events(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            version="v2"
        ):
            kind = event.get("event")
            
            # Stream LLM generated tokens
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    payload = json.dumps({"chunk": chunk.content})
                    yield f"data: {payload}\n\n"
                    # 40ms delay per token for natural, visible typing speed
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
    return {"status": "healthy", "service": "AI Support Agent"}