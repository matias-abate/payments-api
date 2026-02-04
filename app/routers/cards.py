from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.card import Card
from app.models.user import User
from app.schemas.card import CardCreate, CardResponse, CardStatusUpdate
from app.auth import get_current_user
from app.services.validators import validate_card_limit

router = APIRouter(prefix="/cards", tags=["cards"])


def mask_card_number(card_number: str) -> str:
    return f"**** **** **** {card_number[-4:]}"


@router.post("/", response_model=CardResponse, status_code=201)
def add_card(card: CardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validar límite de tarjetas
    validate_card_limit(current_user, db)
    
    db_card = Card(
        user_id=current_user.id,
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
def list_my_cards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Card).filter(Card.user_id == current_user.id).all()


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    return card


@router.patch("/{card_id}/status", response_model=CardResponse)
def update_card_status(
    card_id: int,
    data: CardStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    
    if card.status == "expired":
        raise HTTPException(status_code=400, detail="No se puede cambiar el estado de una tarjeta expirada")
    
    card.status = data.status
    db.commit()
    db.refresh(card)
    return card


@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    db.delete(card)
    db.commit()