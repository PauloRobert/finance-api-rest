import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PixKeyType(str, enum.Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    RANDOM = "RANDOM"


class PixTransferStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"


class PixKey(Base):
    """Chaves Pix do usuário"""

    __tablename__ = "pix_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key_type = Column(SAEnum(PixKeyType), nullable=False)
    key_value = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class PixTransfer(Base):
    """Transferências Pix"""

    __tablename__ = "pix_transfers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_key = Column(String(255), nullable=False)
    receiver_name = Column(String(150), nullable=True)
    receiver_bank = Column(String(150), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum(PixTransferStatus),
        default=PixTransferStatus.COMPLETED,
        nullable=False,
    )
    scheduled_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Favorito
    is_favorite = Column(Boolean, default=False)
