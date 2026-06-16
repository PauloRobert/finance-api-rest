from typing import Optional
from pydantic import BaseModel, Field


# ── Deposit ─────────────────────────────────────────────

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)
    deposit_type: str = Field("PIX", pattern="^(BOLETO|PIX|TED)$")
    description: Optional[str] = Field(None, max_length=255)

class DepositResponse(BaseModel):
    id: str; amount: float; deposit_type: str; status: str
    description: Optional[str] = None; created_at: str
    class Config: from_attributes = True

class DepositListResponse(BaseModel):
    deposits: list[DepositResponse] = []; total: int = 0

# ── Payment ─────────────────────────────────────────────

class PaymentRequest(BaseModel):
    barcode: Optional[str] = Field(None, max_length=100)
    payee_name: str = Field(..., min_length=2)
    amount: float = Field(..., gt=0)
    due_date: Optional[str] = None
    payment_type: str = Field("BOLETO", pattern="^(BOLETO|UTILITY|TAX)$")
    description: Optional[str] = Field(None, max_length=255)

class PaymentResponse(BaseModel):
    id: str; barcode: Optional[str] = None; payee_name: str
    amount: float; due_date: Optional[str] = None
    payment_type: str; status: str
    description: Optional[str] = None; created_at: str
    class Config: from_attributes = True

class PaymentListResponse(BaseModel):
    payments: list[PaymentResponse] = []; total: int = 0

# ── Card ────────────────────────────────────────────────

class CardResponse(BaseModel):
    id: str; card_name: str; last_four: str; card_type: str
    status: str; credit_limit: float; available_limit: float
    due_day: str; is_contactless: bool; is_international: bool
    class Config: from_attributes = True

class CardCreateRequest(BaseModel):
    card_name: str = Field(..., min_length=2, max_length=100)
    card_type: str = Field("DEBIT", pattern="^(DEBIT|CREDIT|VIRTUAL)$")
    credit_limit: float = Field(0.0, ge=0)

class CardUpdateRequest(BaseModel):
    is_contactless: Optional[bool] = None
    is_international: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|BLOCKED)$")

class CardTransactionResponse(BaseModel):
    id: str; merchant: str; amount: float; installments: str
    category: Optional[str] = None; created_at: str
    class Config: from_attributes = True

class CardTransactionListResponse(BaseModel):
    transactions: list[CardTransactionResponse] = []; total: int = 0

# ── Investment ──────────────────────────────────────────

class InvestmentResponse(BaseModel):
    id: str; name: str; investment_type: str
    amount_invested: float; current_value: float
    annual_rate: float; maturity_date: Optional[str] = None
    status: str; created_at: str
    class Config: from_attributes = True

class InvestmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    investment_type: str = Field(..., pattern="^(CDB|LCI|LCA|TESOURO|FUNDO|ACAO)$")
    amount: float = Field(..., gt=0)
    maturity_date: Optional[str] = None

class InvestmentListResponse(BaseModel):
    investments: list[InvestmentResponse] = []; total: int = 0

class InvestmentDashboardResponse(BaseModel):
    total_invested: float = 0.0
    total_current_value: float = 0.0
    total_profit: float = 0.0
    profit_percentage: float = 0.0
    investments_count: int = 0
