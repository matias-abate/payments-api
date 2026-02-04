from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.card import Card
from app.schemas.card import CardCreate, CardResponse

router = APIRouter(prefix="/users/{user_id}/cards", tags=["cards"])


def mask_card_number(card_number: str) -> str:
    """Enmascara el número de tarjeta mostrando solo los últimos 4 dígitos"""
    return f"**** **** **** {card_number[-4:]}"


@router.post("/", response_model=CardResponse, status_code=201)
def add_card(user_id: int, card: CardCreate, db: Session = Depends(get_db)):
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db_card = Card(
        user_id=user_id,
        card_number_masked=mask_card_number(card.card_number),
        card_type=card.card_type.lower(),
        expiration_month=card.expiration_month,
        expiration_year=card.expiration_year,
        holder_name=card.holder_name
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.get("/", response_model=list[CardResponse])
def list_user_cards(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user.cards


@router.delete("/{card_id}", status_code=204)
def delete_card(user_id: int, card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == user_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    db.delete(card)
    db.commit()