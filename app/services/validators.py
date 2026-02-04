from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.user import User
from app.models.card import Card
from app.models.payment import Payment
from app.models.transfer import Transfer
from app.auth import get_user_limits


def validate_card_not_expired(card: Card) -> None:
    """Valida que la tarjeta no esté expirada"""
    now = datetime.utcnow()
    
    # La tarjeta expira al final del mes de expiración
    if card.expiration_year < now.year:
        raise HTTPException(status_code=400, detail="Tarjeta expirada")
    
    if card.expiration_year == now.year and card.expiration_month < now.month:
        raise HTTPException(status_code=400, detail="Tarjeta expirada")


def validate_card_status(card: Card) -> None:
    """Valida que la tarjeta esté activa"""
    if card.status == "blocked":
        raise HTTPException(status_code=400, detail="Tarjeta bloqueada")
    if card.status == "expired":
        raise HTTPException(status_code=400, detail="Tarjeta expirada")
    if card.status != "active":
        raise HTTPException(status_code=400, detail=f"Tarjeta no disponible: {card.status}")


def validate_card_limit(user: User, db: Session) -> None:
    """Valida que el usuario no exceda su límite de tarjetas"""
    limits = get_user_limits(user)
    active_cards = db.query(Card).filter(
        Card.user_id == user.id,
        Card.status == "active"
    ).count()
    
    if active_cards >= limits["max_cards"]:
        raise HTTPException(
            status_code=400,
            detail=f"Límite de tarjetas alcanzado ({limits['max_cards']}). Nivel: {user.verification_level}"
        )


def validate_user_balance(user: User, amount: float) -> None:
    """Valida que el usuario tenga balance suficiente"""
    if user.balance < amount:
        raise HTTPException(
            status_code=400,
            detail=f"Balance insuficiente. Disponible: {user.balance}, Requerido: {amount}"
        )


def validate_user_active(user: User) -> None:
    """Valida que el usuario esté activo"""
    if user.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Usuario {user.status}. No puede realizar operaciones."
        )


def validate_transaction_limit(user: User, amount: float) -> None:
    """Valida que el monto no exceda el límite por transacción"""
    limits = get_user_limits(user)
    
    if amount > limits["max_transaction"]:
        raise HTTPException(
            status_code=400,
            detail=f"Monto excede límite por transacción (${limits['max_transaction']}). Nivel: {user.verification_level}"
        )


def validate_daily_limit(user: User, amount: float, db: Session) -> None:
    """Valida que no se exceda el límite diario"""
    limits = get_user_limits(user)
    today = datetime.utcnow().date()
    
    # Sumar pagos del día
    daily_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.user_id == user.id,
        Payment.status == "approved",
        func.date(Payment.created_at) == today
    ).scalar() or 0
    
    # Sumar transferencias enviadas del día
    daily_transfers = db.query(func.sum(Transfer.amount)).filter(
        Transfer.sender_id == user.id,
        Transfer.status == "completed",
        func.date(Transfer.created_at) == today
    ).scalar() or 0
    
    total_today = daily_payments + daily_transfers + amount
    
    if total_today > limits["daily_limit"]:
        remaining = limits["daily_limit"] - (daily_payments + daily_transfers)
        raise HTTPException(
            status_code=400,
            detail=f"Límite diario excedido. Disponible hoy: ${max(0, remaining):.2f}"
        )


def validate_monthly_limit(user: User, amount: float, db: Session) -> None:
    """Valida que no se exceda el límite mensual"""
    limits = get_user_limits(user)
    now = datetime.utcnow()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Sumar pagos del mes
    monthly_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.user_id == user.id,
        Payment.status == "approved",
        Payment.created_at >= first_day_of_month
    ).scalar() or 0
    
    # Sumar transferencias enviadas del mes
    monthly_transfers = db.query(func.sum(Transfer.amount)).filter(
        Transfer.sender_id == user.id,
        Transfer.status == "completed",
        Transfer.created_at >= first_day_of_month
    ).scalar() or 0
    
    total_month = monthly_payments + monthly_transfers + amount
    
    if total_month > limits["monthly_limit"]:
        remaining = limits["monthly_limit"] - (monthly_payments + monthly_transfers)
        raise HTTPException(
            status_code=400,
            detail=f"Límite mensual excedido. Disponible este mes: ${max(0, remaining):.2f}"
        )


def validate_all_payment_limits(user: User, card: Card, amount: float, db: Session) -> None:
    """Ejecuta todas las validaciones para un pago"""
    validate_user_active(user)
    validate_card_status(card)
    validate_card_not_expired(card)
    validate_transaction_limit(user, amount)
    validate_daily_limit(user, amount, db)
    validate_monthly_limit(user, amount, db)


def validate_all_transfer_limits(sender: User, receiver: User, amount: float, db: Session) -> None:
    """Ejecuta todas las validaciones para una transferencia"""
    validate_user_active(sender)
    validate_user_active(receiver)
    validate_user_balance(sender, amount)
    validate_transaction_limit(sender, amount)
    validate_daily_limit(sender, amount, db)
    validate_monthly_limit(sender, amount, db)