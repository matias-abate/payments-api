from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.models.transfer import Transfer
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, UserLimits, BalanceUpdate
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user, get_user_limits

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if user.status != "active":
        raise HTTPException(status_code=403, detail=f"Usuario {user.status}")
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/limits", response_model=UserLimits)
def get_my_limits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    limits = get_user_limits(current_user)
    now = datetime.utcnow()
    today = now.date()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calcular uso diario
    daily_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.user_id == current_user.id,
        Payment.status == "approved",
        func.date(Payment.created_at) == today
    ).scalar() or 0
    
    daily_transfers = db.query(func.sum(Transfer.amount)).filter(
        Transfer.sender_id == current_user.id,
        Transfer.status == "completed",
        func.date(Transfer.created_at) == today
    ).scalar() or 0
    
    daily_used = daily_payments + daily_transfers
    
    # Calcular uso mensual
    monthly_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.user_id == current_user.id,
        Payment.status == "approved",
        Payment.created_at >= first_day_of_month
    ).scalar() or 0
    
    monthly_transfers = db.query(func.sum(Transfer.amount)).filter(
        Transfer.sender_id == current_user.id,
        Transfer.status == "completed",
        Transfer.created_at >= first_day_of_month
    ).scalar() or 0
    
    monthly_used = monthly_payments + monthly_transfers
    
    return UserLimits(
        max_cards=limits["max_cards"],
        max_transaction=limits["max_transaction"],
        daily_limit=limits["daily_limit"],
        monthly_limit=limits["monthly_limit"],
        daily_used=daily_used,
        monthly_used=monthly_used,
        daily_remaining=max(0, limits["daily_limit"] - daily_used),
        monthly_remaining=max(0, limits["monthly_limit"] - monthly_used)
    )


@router.post("/me/deposit", response_model=UserResponse)
def deposit(data: BalanceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Depositar dinero en la cuenta (simula carga de saldo)"""
    current_user.balance += data.amount
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user