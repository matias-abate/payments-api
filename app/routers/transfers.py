from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferResponse, TransferDetail
from app.services.validators import validate_all_transfer_limits
from app.auth import get_current_user

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("/", response_model=TransferResponse, status_code=201)
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # No puede transferirse a sí mismo
    if transfer.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes transferirte a ti mismo")
    
    # Verificar que el receptor existe
    receiver = db.query(User).filter(User.id == transfer.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Usuario receptor no encontrado")
    
    # Ejecutar todas las validaciones
    validate_all_transfer_limits(current_user, receiver, transfer.amount, db)
    
    # Realizar la transferencia
    current_user.balance -= transfer.amount
    receiver.balance += transfer.amount
    
    db_transfer = Transfer(
        sender_id=current_user.id,
        receiver_id=transfer.receiver_id,
        amount=transfer.amount,
        currency=transfer.currency,
        status="completed",
        description=transfer.description,
        completed_at=datetime.utcnow()
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer


@router.get("/", response_model=list[TransferResponse])
def list_my_transfers(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transfer).filter(
        (Transfer.sender_id == current_user.id) | (Transfer.receiver_id == current_user.id)
    )
    if status:
        query = query.filter(Transfer.status == status)
    return query.offset(skip).limit(limit).all()


@router.get("/sent", response_model=list[TransferResponse])
def get_sent_transfers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Transfer).filter(Transfer.sender_id == current_user.id).all()


@router.get("/received", response_model=list[TransferResponse])
def get_received_transfers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Transfer).filter(Transfer.receiver_id == current_user.id).all()


@router.get("/{transfer_id}", response_model=TransferDetail)
def get_transfer(transfer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transferencia no encontrada")
    
    # Solo puede ver transferencias donde participa
    if transfer.sender_id != current_user.id and transfer.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta transferencia")
    
    return TransferDetail(
        id=transfer.id,
        sender_id=transfer.sender_id,
        receiver_id=transfer.receiver_id,
        amount=transfer.amount,
        currency=transfer.currency,
        status=transfer.status,
        description=transfer.description,
        created_at=transfer.created_at,
        completed_at=transfer.completed_at,
        sender_name=transfer.sender.name,
        receiver_name=transfer.receiver.name
    )