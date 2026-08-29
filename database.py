import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./orders.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    item = Column(String, nullable=False)
    status = Column(String, nullable=False)
    delivery_date = Column(String, nullable=False)

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issue_description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Order).first():
        sample_orders = [
            Order(id="ORD101", item="Wireless Headphones", status="Shipped", delivery_date="Tomorrow at 2:00 PM"),
            Order(id="ORD102", item="Mechanical Keyboard", status="Processing", delivery_date="Pending"),
            Order(id="ORD103", item="USB-C Hub", status="Delivered", delivery_date="Delivered Yesterday"),
        ]
        db.add_all(sample_orders)
        db.commit()
    db.close()