import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from app.database import Base


# ── Deposit ─────────────────────────────────────────────

class DepositType(str, enum.Enum):
    BOLETO = "BOLETO"
    PIX = "PIX"
    TED = "TED"


class DepositStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    deposit_type = Column(SAEnum(DepositType), default=DepositType.PIX)
    status = Column(SAEnum(DepositStatus), default=DepositStatus.COMPLETED)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── Payment (Boleto / Conta) ────────────────────────────

class PaymentType(str, enum.Enum):
    BOLETO = "BOLETO"
    UTILITY = "UTILITY"
    TAX = "TAX"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SCHEDULED = "SCHEDULED"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    barcode = Column(String(100), nullable=True)
    payee_name = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(String(20), nullable=True)
    payment_type = Column(SAEnum(PaymentType), default=PaymentType.BOLETO)
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.COMPLETED)
    description = Column(Text, nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── Card ────────────────────────────────────────────────

class CardType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    VIRTUAL = "VIRTUAL"


class CardStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    card_name = Column(String(100), nullable=False)
    last_four = Column(String(4), nullable=False)
    card_type = Column(SAEnum(CardType), default=CardType.DEBIT)
    status = Column(SAEnum(CardStatus), default=CardStatus.ACTIVE)
    credit_limit = Column(Float, default=0.0)
    available_limit = Column(Float, default=0.0)
    due_day = Column(String(2), default="10")
    is_contactless = Column(Boolean, default=True)
    is_international = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class CardTransaction(Base):
    __tablename__ = "card_transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    card_id = Column(String, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    installments = Column(String(10), default="1/1")
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── Investment ──────────────────────────────────────────

class InvestmentType(str, enum.Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO = "TESOURO"
    FUNDO = "FUNDO"
    ACAO = "ACAO"


class InvestmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REDEEMED = "REDEEMED"
    MATURED = "MATURED"


class Investment(Base):
    __tablename__ = "investments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    investment_type = Column(SAEnum(InvestmentType), default=InvestmentType.CDB)
    amount_invested = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    annual_rate = Column(Float, default=0.0)
    maturity_date = Column(String(20), nullable=True)
    status = Column(SAEnum(InvestmentStatus), default=InvestmentStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
