from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.card import Card
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_processor import simulate_payment
from app.services.validators import validate_all_payment_limits
from app.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verificar que la tarjeta existe y pertenece al usuario
    card = db.query(Card).filter(
        Card.id == payment.card_id,
        Card.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    
    # Ejecutar todas las validaciones
    validate_all_payment_limits(current_user, card, payment.amount, db)
    
    # Simular procesamiento del pago
    result = simulate_payment(payment.amount, card.card_type)
    
    db_payment = Payment(
        user_id=current_user.id,
        card_id=payment.card_id,
        amount=payment.amount,
        currency=payment.currency,
        status=result["status"],
        description=payment.description
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/", response_model=list[PaymentResponse])
def list_my_payments(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Payment).filter(Payment.user_id == current_user.id)
    if status:
        query = query.filter(Payment.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment