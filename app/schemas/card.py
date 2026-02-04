from pydantic import BaseModel, field_validator
from datetime import datetime


class CardCreate(BaseModel):
    card_number: str
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

    @field_validator("expiration_year")
    @classmethod
    def validate_year(cls, v):
        from datetime import datetime
        current_year = datetime.utcnow().year
        if v < current_year or v > current_year + 20:
            raise ValueError(f"Año debe estar entre {current_year} y {current_year + 20}")
        return v


class CardResponse(BaseModel):
    id: int
    card_number_masked: str
    card_type: str
    expiration_month: int
    expiration_year: int
    holder_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CardStatusUpdate(BaseModel):
    status: str
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["active", "blocked"]
        if v not in allowed:
            raise ValueError(f"Status debe ser uno de: {allowed}")
        return v