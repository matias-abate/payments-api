from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    balance: float
    status: str
    verification_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserLimits(BaseModel):
    max_cards: int
    max_transaction: float
    daily_limit: float
    monthly_limit: float
    daily_used: float
    monthly_used: float
    daily_remaining: float
    monthly_remaining: float


class Token(BaseModel):
    access_token: str
    token_type: str


class BalanceUpdate(BaseModel):
    amount: float
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return round(v, 2)