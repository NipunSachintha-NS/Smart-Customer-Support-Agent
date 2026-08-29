import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# 1. Store Policies & FAQ Knowledge Base Data
POLICIES_DATA = [
    Document(
        page_content="TechGear Return Policy: Customers can return unopened items within 30 days of delivery for a full refund. Opened or used electronics must be returned within 14 days and may incur a 10% restocking fee. Shipping fees are non-refundable.",
        metadata={"topic": "returns", "policy_id": "RET-01"}
    ),
    Document(
        page_content="TechGear Warranty Guidelines: All hardware and electronics come with a standard 1-year limited manufacturer warranty covering mechanical or electrical defects. Physical damages, liquid spills, or unauthorized modifications are not covered under warranty.",
        metadata={"topic": "warranty", "policy_id": "WAR-01"}
    ),
    Document(
        page_content="TechGear Shipping & Delivery: Standard domestic shipping takes 2-4 business days. Express shipping delivers within 1-2 business days. International shipping takes 7-14 business days. Free standard shipping applies to all orders over $50.",
        metadata={"topic": "shipping", "policy_id": "SHP-01"}
    ),
    Document(
        page_content="Order Cancellation Policy: Orders can only be cancelled while in 'Processing' status. Once an order is marked as 'Shipped' or 'Delivered', it cannot be cancelled and the customer must initiate a standard return after delivery.",
        metadata={"topic": "cancellation", "policy_id": "CAN-01"}
    ),
]

# 2. Vector DB Initialize & Seed Helper
def get_vector_store():
    persist_directory = "./chroma_db"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Check if vector DB already exists locally
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    # Initialize and persist embeddings
    vector_store = Chroma.from_documents(
        documents=POLICIES_DATA,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vector_store

# Create retriever instance
vector_store = get_vector_store()
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

def search_store_knowledge(query: str) -> str:
    """Retrieve relevant policies based on semantic similarity."""
    docs = retriever.invoke(query)
    if not docs:
        return "No specific store policy found regarding this topic."
    return "\n\n".join([doc.page_content for doc in docs])