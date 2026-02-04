from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class TransferCreate(BaseModel):
    receiver_id: int
    amount: float
    currency: str = "USD"
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return round(v, 2)


class TransferResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TransferDetail(TransferResponse):
    sender_name: str
    receiver_name: str