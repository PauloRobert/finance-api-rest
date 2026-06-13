from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    """Tipo de transação"""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionCreate(BaseModel):
    """Schema para criação de transação"""
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    date: str = Field(..., description="Data no formato ISO 8601 (ex: 2026-06-13T10:30:00)")
    type: TransactionType


class TransactionUpdate(BaseModel):
    """Schema para atualização de transação"""
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = None
    type: Optional[TransactionType] = None


class TransactionResponse(BaseModel):
    """Schema de resposta de transação"""
    id: str
    description: str
    amount: float
    date: str
    type: TransactionType

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema de resposta para lista de transações"""
    transactions: list[TransactionResponse]
    total: int

