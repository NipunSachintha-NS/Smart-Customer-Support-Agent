import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Initialize FastAPI Application
app = FastAPI(
    title="Customer Support AI Agent API",
    description="Production REST API for TechGear Customer Support Agent",
    version="1.0.0"
)

# Add CORS Middleware right after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any frontend port (e.g., Vite: 5173, CRA: 3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Provide your OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mock Database & Custom Tools
ORDERS_DB = {
    "ORD101": {"item": "Wireless Headphones", "status": "Shipped", "delivery_date": "Tomorrow, 2:00 PM"},
    "ORD102": {"item": "Mechanical Keyboard", "status": "Processing", "delivery_date": "Friday, 5:00 PM"},
    "ORD103": {"item": "USB-C Hub", "status": "Delivered", "delivery_date": "Delivered on Monday"}
}

@tool
def get_order_status(order_id: str) -> str:
    """Retrieve shipping and delivery information for a specific order ID."""
    order = ORDERS_DB.get(order_id.upper())
    if order:
        return f"Order {order_id.upper()}: Item: {order['item']} | Status: {order['status']} | Delivery: {order['delivery_date']}"
    return f"Error: Order ID '{order_id}' was not found in our system."

@tool
def cancel_order(order_id: str) -> str:
    """Cancel an existing order if it is still in Processing status."""
    order = ORDERS_DB.get(order_id.upper())
    if not order:
        return f"Error: Order ID '{order_id}' does not exist."
    if order["status"] == "Shipped":
        return f"Cannot cancel Order {order_id.upper()}. It has already been shipped."
    elif order["status"] == "Processing":
        order["status"] = "Cancelled"
        return f"Success: Order {order_id.upper()} has been cancelled successfully."
    return f"Order {order_id.upper()} cannot be cancelled as it is already {order['status']}."

tools = [get_order_status, cancel_order]

# Initialize Agent & Memory
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.2
)

memory = MemorySaver()

system_prompt = (
    "You are a helpful Customer Support Agent for 'TechGear Store'.\n"
    "Help customers check order statuses or cancel orders using tools.\n"
    "Always maintain a polite tone and reply in English or Sinhala depending on the user's language."
)

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt,
    checkpointer=memory
)

# Pydantic Models for Request & Response Validation
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    session_id: str
    response: str

# REST API Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring uptime."""
    return {"status": "healthy", "service": "AI Support Agent"}

@app.post("/chat", response_model=ChatResponse)
def chat_with_agent(payload: ChatRequest):
    """Chat endpoint to interact with the AI Agent with session memory."""
    try:
        config = {"configurable": {"thread_id": payload.session_id}}
        
        agent_output = agent.invoke(
            {"messages": [("user", payload.message)]},
            config=config
        )
        
        reply = agent_output["messages"][-1].content
        return ChatResponse(session_id=payload.session_id, response=reply)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))