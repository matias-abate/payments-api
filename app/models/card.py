from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number_masked = Column(String, nullable=False)  # ej: **** **** **** 1234
    card_type = Column(String, nullable=False)  # visa, mastercard, amex
    expiration_month = Column(Integer, nullable=False)
    expiration_year = Column(Integer, nullable=False)
    holder_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cards")
    payments = relationship("Payment", back_populates="card")