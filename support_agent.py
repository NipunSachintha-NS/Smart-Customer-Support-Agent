import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

OPENAI_API_KEY = "API_KEY"  

# Mock Database 
ORDERS_DB = {
    "ORD101": {"item": "Wireless Headphones", "status": "Shipped", "delivery_date": "Tomorrow, 2:00 PM"},
    "ORD102": {"item": "Mechanical Keyboard", "status": "Processing", "delivery_date": "Friday, 5:00 PM"},
    "ORD103": {"item": "USB-C Hub", "status": "Delivered", "delivery_date": "Delivered on Monday"}
}

@tool
def get_order_status(order_id: str) -> str:
    """Retrieve shipping and delivery information for a specific order ID (e.g., ORD101)."""
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


llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.2
)

memory = MemorySaver()

system_prompt = (
    "You are a helpful, polite Customer Support Agent for 'TechGear Store'.\n"
    "Help customers check order statuses or cancel orders using the available tools.\n"
    "Always maintain a polite tone and reply in English or Sinhala depending on the user's language."
)

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt,
    checkpointer=memory
)


print("\n--- TechGear Customer Support Agent Ready! ---")
print("Type 'exit' to end the conversation.\n")


config = {"configurable": {"thread_id": "customer_session_1"}}

while True:
    user_input = input("Customer: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Agent: Thank you for contacting TechGear Store. Have a great day!")
        break

    response = agent.invoke(
        {"messages": [("user", user_input)]},
        config=config
    )
    print(f"Agent: {response['messages'][-1].content}\n")