import enum
import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, String
from sqlalchemy.sql import func

from app.database import Base


class TransactionType(str, enum.Enum):
    """Tipo de transação: entrada ou saída"""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Transaction(Base):
    """Modelo de transação financeira"""

    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # ISO 8601 format
    type = Column(SAEnum(TransactionType), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
