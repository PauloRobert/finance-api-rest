import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from app.database import Base


class AccountType(str, enum.Enum):
    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    SALARIO = "SALARIO"
    PAGAMENTO = "PAGAMENTO"


class TransferStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"


class Beneficiary(Base):
    """Favorecidos para transferência"""

    __tablename__ = "beneficiaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(150), nullable=False)
    cpf_cnpj = Column(String(20), nullable=True)
    bank_name = Column(String(150), nullable=False)
    agency = Column(String(10), nullable=True)
    account = Column(String(20), nullable=False)
    account_type = Column(SAEnum(AccountType), default=AccountType.CORRENTE)
    nickname = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class BankTransfer(Base):
    """Transferências bancárias"""

    __tablename__ = "bank_transfers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    beneficiary_id = Column(
        String, ForeignKey("beneficiaries.id"), nullable=True
    )
    receiver_name = Column(String(150), nullable=False)
    receiver_bank = Column(String(150), nullable=False)
    receiver_agency = Column(String(10), nullable=True)
    receiver_account = Column(String(20), nullable=False)
    receiver_account_type = Column(SAEnum(AccountType), default=AccountType.CORRENTE)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum(TransferStatus), default=TransferStatus.COMPLETED, nullable=False
    )
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
