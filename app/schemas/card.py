from pydantic import BaseModel, field_validator
from datetime import datetime


class CardCreate(BaseModel):
    card_number: str  # se recibe completo, se guarda enmascarado
    card_type: str
    expiration_month: int
    expiration_year: int
    holder_name: str

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v):
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError("Número de tarjeta inválido")
        return cleaned

    @field_validator("expiration_month")
    @classmethod
    def validate_month(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Mes debe estar entre 1 y 12")
        return v


class CardResponse(BaseModel):
    id: int
    card_number_masked: str
    card_type: str
    expiration_month: int
    expiration_year: int
    holder_name: str
    created_at: datetime

    class Config:
        from_attributes = True