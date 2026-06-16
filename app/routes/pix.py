import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.pix import PixKey, PixKeyType, PixTransfer, PixTransferStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserProfile
from app.schemas.pix import (
    PixDashboardResponse,
    PixFavoriteResponse,
    PixKeyCreate,
    PixKeyLookupResponse,
    PixKeyResponse,
    PixSendRequest,
    PixTransferListResponse,
    PixTransferResponse,
)

router = APIRouter(prefix="/pix", tags=["Pix"])


# ── Dashboard ───────────────────────────────────────────


@router.get("/dashboard", response_model=PixDashboardResponse, summary="Dashboard Pix")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Saldo: soma entradas - soma saídas
    income = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.INCOME,
        )
        .scalar()
    )
    expense = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .scalar()
    )
    balance = income - expense

    # Total Pix enviado/recebido no mês
    now = datetime.now(timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_sent = (
        db.query(sa_func.coalesce(sa_func.sum(PixTransfer.amount), 0))
        .filter(
            PixTransfer.sender_id == current_user.id,
            PixTransfer.status == PixTransferStatus.COMPLETED,
            PixTransfer.created_at >= first_day,
        )
        .scalar()
    )

    # Recebidos: buscar chaves do usuário e filtrar transferências para essas chaves
    user_keys = [
        k.key_value
        for k in db.query(PixKey).filter(PixKey.user_id == current_user.id).all()
    ]
    total_received = 0.0
    if user_keys:
        total_received = (
            db.query(sa_func.coalesce(sa_func.sum(PixTransfer.amount), 0))
            .filter(
                PixTransfer.receiver_key.in_(user_keys),
                PixTransfer.status == PixTransferStatus.COMPLETED,
                PixTransfer.created_at >= first_day,
            )
            .scalar()
        )

    # Uso diário
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_used = (
        db.query(sa_func.coalesce(sa_func.sum(PixTransfer.amount), 0))
        .filter(
            PixTransfer.sender_id == current_user.id,
            PixTransfer.status == PixTransferStatus.COMPLETED,
            PixTransfer.created_at >= today_start,
        )
        .scalar()
    )

    keys_count = (
        db.query(PixKey)
        .filter(PixKey.user_id == current_user.id, PixKey.is_active == True)
        .count()
    )

    return PixDashboardResponse(
        balance=balance,
        daily_limit=20000.0,
        daily_used=daily_used,
        pix_active=True,
        total_sent_month=total_sent,
        total_received_month=total_received,
        keys_count=keys_count,
    )


# ── Keys CRUD ───────────────────────────────────────────


@router.get("/keys", response_model=list[PixKeyResponse], summary="Listar chaves Pix")
def list_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keys = (
        db.query(PixKey)
        .filter(PixKey.user_id == current_user.id, PixKey.is_active == True)
        .all()
    )
    return keys


@router.post(
    "/keys",
    response_model=PixKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar chave Pix",
)
def create_key(
    data: PixKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Limite de 5 chaves
    count = (
        db.query(PixKey)
        .filter(PixKey.user_id == current_user.id, PixKey.is_active == True)
        .count()
    )
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limite de 5 chaves Pix atingido",
        )

    # Verificar duplicidade
    existing = db.query(PixKey).filter(PixKey.key_value == data.key_value).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta chave já está cadastrada",
        )

    # Gerar chave aleatória se tipo RANDOM
    key_value = data.key_value
    if data.key_type == "RANDOM":
        key_value = str(uuid.uuid4())

    key = PixKey(
        user_id=current_user.id,
        key_type=PixKeyType(data.key_type),
        key_value=key_value,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@router.delete("/keys/{key_id}", status_code=status.HTTP_200_OK, summary="Excluir chave Pix")
def delete_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    key = (
        db.query(PixKey)
        .filter(PixKey.id == key_id, PixKey.user_id == current_user.id)
        .first()
    )
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chave não encontrada"
        )
    key.is_active = False
    db.commit()
    return {"message": "Chave excluída com sucesso"}


# ── Key Lookup ──────────────────────────────────────────


@router.get(
    "/lookup", response_model=PixKeyLookupResponse, summary="Consultar chave Pix"
)
def lookup_key(
    key: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pix_key = db.query(PixKey).filter(PixKey.key_value == key, PixKey.is_active == True).first()
    if not pix_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chave Pix não encontrada",
        )

    owner = db.query(User).filter(User.id == pix_key.user_id).first()
    owner_name = owner.username if owner else "Desconhecido"

    # Tentar obter display_name do perfil
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == pix_key.user_id)
        .first()
    )
    if profile and profile.display_name:
        owner_name = profile.display_name

    return PixKeyLookupResponse(
        key_value=key,
        owner_name=owner_name,
        bank="IF Bank",
    )


# ── Send Pix ────────────────────────────────────────────


@router.post(
    "/send",
    response_model=PixTransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar Pix",
)
def send_pix(
    data: PixSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verificar chave destino
    pix_key = (
        db.query(PixKey)
        .filter(PixKey.key_value == data.receiver_key, PixKey.is_active == True)
        .first()
    )
    if not pix_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chave Pix do destinatário não encontrada",
        )

    # Não pode enviar para si mesmo
    if pix_key.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível enviar Pix para si mesmo",
        )

    # Verificar saldo
    income = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.INCOME,
        )
        .scalar()
    )
    expense = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .scalar()
    )
    balance = income - expense
    if balance < data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo insuficiente",
        )

    # Verificar limite diário
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    daily_used = (
        db.query(sa_func.coalesce(sa_func.sum(PixTransfer.amount), 0))
        .filter(
            PixTransfer.sender_id == current_user.id,
            PixTransfer.status == PixTransferStatus.COMPLETED,
            PixTransfer.created_at >= today_start,
        )
        .scalar()
    )
    if daily_used + data.amount > 20000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limite diário de Pix excedido",
        )

    # Buscar nome do destinatário
    owner = db.query(User).filter(User.id == pix_key.user_id).first()
    receiver_name = owner.username if owner else "Desconhecido"
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == pix_key.user_id)
        .first()
    )
    if profile and profile.display_name:
        receiver_name = profile.display_name

    # Criar transferência
    transfer = PixTransfer(
        sender_id=current_user.id,
        receiver_key=data.receiver_key,
        receiver_name=receiver_name,
        receiver_bank="IF Bank",
        amount=data.amount,
        description=data.description,
        status=PixTransferStatus.COMPLETED,
    )
    db.add(transfer)

    # Criar transação de saída para o remetente
    tx_out = Transaction(
        user_id=current_user.id,
        description=f"Pix enviado - {receiver_name}",
        amount=data.amount,
        date=now.isoformat(),
        type=TransactionType.EXPENSE,
    )
    db.add(tx_out)

    # Criar transação de entrada para o destinatário
    sender_name = current_user.username
    sender_profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )
    if sender_profile and sender_profile.display_name:
        sender_name = sender_profile.display_name

    tx_in = Transaction(
        user_id=pix_key.user_id,
        description=f"Pix recebido - {sender_name}",
        amount=data.amount,
        date=now.isoformat(),
        type=TransactionType.INCOME,
    )
    db.add(tx_in)

    db.commit()
    db.refresh(transfer)

    return PixTransferResponse(
        id=transfer.id,
        receiver_key=transfer.receiver_key,
        receiver_name=transfer.receiver_name,
        receiver_bank=transfer.receiver_bank,
        amount=transfer.amount,
        description=transfer.description,
        status=transfer.status.value,
        created_at=transfer.created_at.isoformat() if transfer.created_at else now.isoformat(),
        is_favorite=transfer.is_favorite,
    )


# ── History ─────────────────────────────────────────────


@router.get(
    "/history",
    response_model=PixTransferListResponse,
    summary="Extrato Pix",
)
def get_history(
    filter_type: str = Query("all", pattern="^(all|sent|received)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_keys = [
        k.key_value
        for k in db.query(PixKey).filter(PixKey.user_id == current_user.id).all()
    ]

    query = db.query(PixTransfer)

    if filter_type == "sent":
        query = query.filter(PixTransfer.sender_id == current_user.id)
    elif filter_type == "received":
        if user_keys:
            query = query.filter(PixTransfer.receiver_key.in_(user_keys))
        else:
            return PixTransferListResponse(transfers=[], total=0)
    else:
        # All: sent or received
        from sqlalchemy import or_

        conditions = [PixTransfer.sender_id == current_user.id]
        if user_keys:
            conditions.append(PixTransfer.receiver_key.in_(user_keys))
        query = query.filter(or_(*conditions))

    transfers = query.order_by(PixTransfer.created_at.desc()).limit(50).all()

    result = []
    for t in transfers:
        result.append(
            PixTransferResponse(
                id=t.id,
                receiver_key=t.receiver_key,
                receiver_name=t.receiver_name,
                receiver_bank=t.receiver_bank,
                amount=t.amount,
                description=t.description,
                status=t.status.value,
                created_at=t.created_at.isoformat() if t.created_at else "",
                is_favorite=t.is_favorite,
            )
        )

    return PixTransferListResponse(transfers=result, total=len(result))


# ── Favorites ───────────────────────────────────────────


@router.get(
    "/favorites",
    response_model=list[PixFavoriteResponse],
    summary="Favoritos Pix",
)
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Pegar os destinatários mais frequentes (últimos 10 distintos)
    transfers = (
        db.query(PixTransfer)
        .filter(PixTransfer.sender_id == current_user.id)
        .order_by(PixTransfer.created_at.desc())
        .limit(50)
        .all()
    )

    seen = {}
    favorites = []
    for t in transfers:
        if t.receiver_key not in seen and len(favorites) < 5:
            seen[t.receiver_key] = True
            favorites.append(
                PixFavoriteResponse(
                    receiver_key=t.receiver_key,
                    receiver_name=t.receiver_name,
                    receiver_bank=t.receiver_bank,
                    last_amount=t.amount,
                )
            )

    return favorites
