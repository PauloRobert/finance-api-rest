from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.transaction import Transaction, TransactionType
from app.models.transfer import AccountType, BankTransfer, Beneficiary, TransferStatus
from app.models.user import User, UserProfile
from app.schemas.transfer import (
    BeneficiaryCreate,
    BeneficiaryResponse,
    TransferDashboardResponse,
    TransferListResponse,
    TransferResponse,
    TransferSendRequest,
)

router = APIRouter(prefix="/transfers", tags=["Transferências"])


# ── Dashboard ───────────────────────────────────────────


@router.get("/dashboard", response_model=TransferDashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == current_user.id, Transaction.type == TransactionType.INCOME)
        .scalar()
    )
    expense = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == current_user.id, Transaction.type == TransactionType.EXPENSE)
        .scalar()
    )
    balance = income - expense

    now = datetime.now(timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_month = (
        db.query(sa_func.coalesce(sa_func.sum(BankTransfer.amount), 0))
        .filter(
            BankTransfer.sender_id == current_user.id,
            BankTransfer.status == TransferStatus.COMPLETED,
            BankTransfer.created_at >= first_day,
        )
        .scalar()
    )

    last_transfer = (
        db.query(BankTransfer)
        .filter(BankTransfer.sender_id == current_user.id, BankTransfer.status == TransferStatus.COMPLETED)
        .order_by(BankTransfer.created_at.desc())
        .first()
    )

    scheduled = (
        db.query(BankTransfer)
        .filter(BankTransfer.sender_id == current_user.id, BankTransfer.status == TransferStatus.SCHEDULED)
        .count()
    )

    return TransferDashboardResponse(
        balance=balance,
        transfer_limit=50000.0,
        last_transfer_date=last_transfer.created_at.isoformat() if last_transfer and last_transfer.created_at else None,
        last_transfer_amount=last_transfer.amount if last_transfer else None,
        total_transferred_month=total_month,
        scheduled_count=scheduled,
    )


# ── Beneficiaries CRUD ──────────────────────────────────


@router.get("/beneficiaries", response_model=list[BeneficiaryResponse])
def list_beneficiaries(
    search: str = Query("", max_length=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Beneficiary).filter(
        Beneficiary.user_id == current_user.id,
        Beneficiary.is_active == True,
    )
    if search:
        query = query.filter(
            Beneficiary.name.ilike(f"%{search}%")
            | Beneficiary.nickname.ilike(f"%{search}%")
        )
    return query.order_by(Beneficiary.name).all()


@router.post("/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(
    data: BeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    beneficiary = Beneficiary(
        user_id=current_user.id,
        name=data.name.strip(),
        cpf_cnpj=data.cpf_cnpj,
        bank_name=data.bank_name.strip(),
        agency=data.agency,
        account=data.account.strip(),
        account_type=AccountType(data.account_type),
        nickname=data.nickname.strip() if data.nickname else None,
    )
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


@router.put("/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(
    beneficiary_id: str,
    data: BeneficiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id, Beneficiary.user_id == current_user.id)
        .first()
    )
    if not b:
        raise HTTPException(status_code=404, detail="Favorecido não encontrado")

    b.name = data.name.strip()
    b.cpf_cnpj = data.cpf_cnpj
    b.bank_name = data.bank_name.strip()
    b.agency = data.agency
    b.account = data.account.strip()
    b.account_type = AccountType(data.account_type)
    b.nickname = data.nickname.strip() if data.nickname else None
    db.commit()
    db.refresh(b)
    return b


@router.delete("/beneficiaries/{beneficiary_id}", status_code=200)
def delete_beneficiary(
    beneficiary_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    b = (
        db.query(Beneficiary)
        .filter(Beneficiary.id == beneficiary_id, Beneficiary.user_id == current_user.id)
        .first()
    )
    if not b:
        raise HTTPException(status_code=404, detail="Favorecido não encontrado")
    b.is_active = False
    db.commit()
    return {"message": "Favorecido excluído"}


# ── Send Transfer ───────────────────────────────────────


@router.post("/send", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def send_transfer(
    data: TransferSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verificar saldo
    income = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == current_user.id, Transaction.type == TransactionType.INCOME)
        .scalar()
    )
    expense = (
        db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0))
        .filter(Transaction.user_id == current_user.id, Transaction.type == TransactionType.EXPENSE)
        .scalar()
    )
    balance = income - expense
    if balance < data.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    now = datetime.now(timezone.utc)

    transfer = BankTransfer(
        sender_id=current_user.id,
        beneficiary_id=data.beneficiary_id,
        receiver_name=data.receiver_name.strip(),
        receiver_bank=data.receiver_bank.strip(),
        receiver_agency=data.receiver_agency,
        receiver_account=data.receiver_account.strip(),
        receiver_account_type=AccountType(data.receiver_account_type),
        amount=data.amount,
        description=data.description,
        status=TransferStatus.COMPLETED,
    )
    db.add(transfer)

    tx_out = Transaction(
        user_id=current_user.id,
        description=f"Transferência - {data.receiver_name.strip()}",
        amount=data.amount,
        date=now.isoformat(),
        type=TransactionType.EXPENSE,
    )
    db.add(tx_out)

    db.commit()
    db.refresh(transfer)

    return TransferResponse(
        id=transfer.id,
        receiver_name=transfer.receiver_name,
        receiver_bank=transfer.receiver_bank,
        receiver_agency=transfer.receiver_agency,
        receiver_account=transfer.receiver_account,
        receiver_account_type=transfer.receiver_account_type.value,
        amount=transfer.amount,
        description=transfer.description,
        status=transfer.status.value,
        created_at=transfer.created_at.isoformat() if transfer.created_at else now.isoformat(),
        beneficiary_id=transfer.beneficiary_id,
    )


# ── History ─────────────────────────────────────────────


@router.get("/history", response_model=TransferListResponse)
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfers = (
        db.query(BankTransfer)
        .filter(BankTransfer.sender_id == current_user.id)
        .order_by(BankTransfer.created_at.desc())
        .limit(50)
        .all()
    )
    result = []
    for t in transfers:
        result.append(
            TransferResponse(
                id=t.id,
                receiver_name=t.receiver_name,
                receiver_bank=t.receiver_bank,
                receiver_agency=t.receiver_agency,
                receiver_account=t.receiver_account,
                receiver_account_type=t.receiver_account_type.value,
                amount=t.amount,
                description=t.description,
                status=t.status.value,
                created_at=t.created_at.isoformat() if t.created_at else "",
                beneficiary_id=t.beneficiary_id,
            )
        )
    return TransferListResponse(transfers=result, total=len(result))
