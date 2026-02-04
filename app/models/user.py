from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, blocked, suspended
    verification_level = Column(String(20), default="basic")  # basic, verified, premium
    created_at = Column(DateTime, default=datetime.utcnow)

    cards = relationship("Card", back_populates="user")
    payments = relationship("Payment", back_populates="user")