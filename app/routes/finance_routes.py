import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.finance import (
    Card, CardStatus, CardTransaction, CardType,
    Deposit, DepositStatus, DepositType,
    Investment, InvestmentStatus, InvestmentType,
    Payment, PaymentStatus, PaymentType,
)
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.finance import (
    CardCreateRequest, CardResponse, CardTransactionListResponse, CardTransactionResponse,
    CardUpdateRequest, DepositListResponse, DepositRequest, DepositResponse,
    InvestmentCreateRequest, InvestmentDashboardResponse, InvestmentListResponse,
    InvestmentResponse, PaymentListResponse, PaymentRequest, PaymentResponse,
)

logger = logging.getLogger(__name__)

# ── Deposit Router ──────────────────────────────────────

deposit_router = APIRouter(prefix="/deposits", tags=["Depósitos"])


@deposit_router.post("/", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
def create_deposit(data: DepositRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} depositing {data.amount} via {data.deposit_type}")
    deposit = Deposit(
        user_id=current_user.id, amount=data.amount,
        deposit_type=DepositType(data.deposit_type),
        status=DepositStatus.COMPLETED, description=data.description,
    )
    db.add(deposit)
    tx = Transaction(
        user_id=current_user.id,
        description=f"Depósito via {data.deposit_type}",
        amount=data.amount, date=datetime.now(timezone.utc).isoformat(),
        type=TransactionType.INCOME,
    )
    db.add(tx)
    db.commit()
    db.refresh(deposit)
    logger.info(f"Deposit {deposit.id} completed for user {current_user.id}")
    return DepositResponse(
        id=deposit.id, amount=deposit.amount, deposit_type=deposit.deposit_type.value,
        status=deposit.status.value, description=deposit.description,
        created_at=deposit.created_at.isoformat() if deposit.created_at else "",
    )


@deposit_router.get("/", response_model=DepositListResponse)
def list_deposits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deposits = db.query(Deposit).filter(Deposit.user_id == current_user.id).order_by(Deposit.created_at.desc()).limit(50).all()
    return DepositListResponse(
        deposits=[DepositResponse(
            id=d.id, amount=d.amount, deposit_type=d.deposit_type.value,
            status=d.status.value, description=d.description,
            created_at=d.created_at.isoformat() if d.created_at else "",
        ) for d in deposits], total=len(deposits),
    )


# ── Payment Router ──────────────────────────────────────

payment_router = APIRouter(prefix="/payments", tags=["Pagamentos"])


@payment_router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(data: PaymentRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} paying {data.amount} to {data.payee_name}")
    # Verificar saldo
    income = db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == TransactionType.INCOME).scalar()
    expense = db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == TransactionType.EXPENSE).scalar()
    if (income - expense) < data.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    payment = Payment(
        user_id=current_user.id, barcode=data.barcode,
        payee_name=data.payee_name.strip(), amount=data.amount,
        due_date=data.due_date, payment_type=PaymentType(data.payment_type),
        status=PaymentStatus.COMPLETED, description=data.description,
    )
    db.add(payment)
    tx = Transaction(
        user_id=current_user.id,
        description=f"Pagamento - {data.payee_name.strip()}",
        amount=data.amount, date=datetime.now(timezone.utc).isoformat(),
        type=TransactionType.EXPENSE,
    )
    db.add(tx)
    db.commit()
    db.refresh(payment)
    logger.info(f"Payment {payment.id} completed for user {current_user.id}")
    return PaymentResponse(
        id=payment.id, barcode=payment.barcode, payee_name=payment.payee_name,
        amount=payment.amount, due_date=payment.due_date,
        payment_type=payment.payment_type.value, status=payment.status.value,
        description=payment.description,
        created_at=payment.created_at.isoformat() if payment.created_at else "",
    )


@payment_router.get("/", response_model=PaymentListResponse)
def list_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).limit(50).all()
    return PaymentListResponse(
        payments=[PaymentResponse(
            id=p.id, barcode=p.barcode, payee_name=p.payee_name,
            amount=p.amount, due_date=p.due_date, payment_type=p.payment_type.value,
            status=p.status.value, description=p.description,
            created_at=p.created_at.isoformat() if p.created_at else "",
        ) for p in payments], total=len(payments),
    )


# ── Card Router ─────────────────────────────────────────

card_router = APIRouter(prefix="/cards", tags=["Cartões"])


@card_router.get("/", response_model=list[CardResponse])
def list_cards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Card).filter(Card.user_id == current_user.id, Card.status != CardStatus.CANCELLED).all()


@card_router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(data: CardCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} creating card {data.card_name}")
    last_four = f"{hash(uuid.uuid4()) % 10000:04d}"
    card = Card(
        user_id=current_user.id, card_name=data.card_name.strip(),
        last_four=last_four, card_type=CardType(data.card_type),
        credit_limit=data.credit_limit, available_limit=data.credit_limit,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@card_router.put("/{card_id}", response_model=CardResponse)
def update_card(card_id: str, data: CardUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    if data.is_contactless is not None:
        card.is_contactless = data.is_contactless
    if data.is_international is not None:
        card.is_international = data.is_international
    if data.status is not None:
        card.status = CardStatus(data.status)
    db.commit()
    db.refresh(card)
    return card


@card_router.delete("/{card_id}", status_code=200)
def cancel_card(card_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    card.status = CardStatus.CANCELLED
    db.commit()
    return {"message": "Cartão cancelado"}


@card_router.get("/{card_id}/transactions", response_model=CardTransactionListResponse)
def list_card_transactions(card_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id, Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Cartão não encontrado")
    txs = db.query(CardTransaction).filter(CardTransaction.card_id == card_id).order_by(CardTransaction.created_at.desc()).limit(50).all()
    return CardTransactionListResponse(
        transactions=[CardTransactionResponse(
            id=t.id, merchant=t.merchant, amount=t.amount,
            installments=t.installments, category=t.category,
            created_at=t.created_at.isoformat() if t.created_at else "",
        ) for t in txs], total=len(txs),
    )


# ── Investment Router ───────────────────────────────────

investment_router = APIRouter(prefix="/investments", tags=["Investimentos"])


@investment_router.get("/dashboard", response_model=InvestmentDashboardResponse)
def investment_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    active = db.query(Investment).filter(
        Investment.user_id == current_user.id, Investment.status == InvestmentStatus.ACTIVE).all()
    total_invested = sum(i.amount_invested for i in active)
    total_current = sum(i.current_value for i in active)
    profit = total_current - total_invested
    pct = (profit / total_invested * 100) if total_invested > 0 else 0
    return InvestmentDashboardResponse(
        total_invested=total_invested, total_current_value=total_current,
        total_profit=profit, profit_percentage=round(pct, 2),
        investments_count=len(active),
    )


@investment_router.get("/", response_model=InvestmentListResponse)
def list_investments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).order_by(Investment.created_at.desc()).all()
    return InvestmentListResponse(
        investments=[InvestmentResponse(
            id=i.id, name=i.name, investment_type=i.investment_type.value,
            amount_invested=i.amount_invested, current_value=i.current_value,
            annual_rate=i.annual_rate, maturity_date=i.maturity_date,
            status=i.status.value,
            created_at=i.created_at.isoformat() if i.created_at else "",
        ) for i in investments], total=len(investments),
    )


@investment_router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def create_investment(data: InvestmentCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.id} investing {data.amount} in {data.investment_type}")
    # Verificar saldo
    income = db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == TransactionType.INCOME).scalar()
    expense = db.query(sa_func.coalesce(sa_func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == current_user.id, Transaction.type == TransactionType.EXPENSE).scalar()
    if (income - expense) < data.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para investir")

    rates = {"CDB": 12.5, "LCI": 10.8, "LCA": 10.5, "TESOURO": 11.2, "FUNDO": 15.0, "ACAO": 18.0}
    rate = rates.get(data.investment_type, 12.0)

    investment = Investment(
        user_id=current_user.id, name=data.name.strip(),
        investment_type=InvestmentType(data.investment_type),
        amount_invested=data.amount, current_value=data.amount,
        annual_rate=rate, maturity_date=data.maturity_date,
    )
    db.add(investment)
    tx = Transaction(
        user_id=current_user.id,
        description=f"Investimento - {data.name.strip()}",
        amount=data.amount, date=datetime.now(timezone.utc).isoformat(),
        type=TransactionType.EXPENSE,
    )
    db.add(tx)
    db.commit()
    db.refresh(investment)
    logger.info(f"Investment {investment.id} created for user {current_user.id}")
    return InvestmentResponse(
        id=investment.id, name=investment.name, investment_type=investment.investment_type.value,
        amount_invested=investment.amount_invested, current_value=investment.current_value,
        annual_rate=investment.annual_rate, maturity_date=investment.maturity_date,
        status=investment.status.value,
        created_at=investment.created_at.isoformat() if investment.created_at else "",
    )


@investment_router.post("/{investment_id}/redeem", response_model=InvestmentResponse)
def redeem_investment(investment_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = db.query(Investment).filter(
        Investment.id == investment_id, Investment.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    if inv.status != InvestmentStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Investimento não está ativo")

    inv.status = InvestmentStatus.REDEEMED
    tx = Transaction(
        user_id=current_user.id,
        description=f"Resgate - {inv.name}",
        amount=inv.current_value, date=datetime.now(timezone.utc).isoformat(),
        type=TransactionType.INCOME,
    )
    db.add(tx)
    db.commit()
    db.refresh(inv)
    logger.info(f"Investment {inv.id} redeemed for user {current_user.id}")
    return InvestmentResponse(
        id=inv.id, name=inv.name, investment_type=inv.investment_type.value,
        amount_invested=inv.amount_invested, current_value=inv.current_value,
        annual_rate=inv.annual_rate, maturity_date=inv.maturity_date,
        status=inv.status.value,
        created_at=inv.created_at.isoformat() if inv.created_at else "",
    )
