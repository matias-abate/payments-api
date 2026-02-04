from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default="pending")
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_transfers")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_transfers")

    __table_args__ = (
        CheckConstraint('sender_id != receiver_id', name='chk_different_users'),
        CheckConstraint('amount > 0', name='chk_positive_amount'),
    )