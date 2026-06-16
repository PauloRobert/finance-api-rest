from typing import Optional

from pydantic import BaseModel, Field


# ── Beneficiary ─────────────────────────────────────────


class BeneficiaryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    cpf_cnpj: Optional[str] = Field(None, max_length=20)
    bank_name: str = Field(..., min_length=2, max_length=150)
    agency: Optional[str] = Field(None, max_length=10)
    account: str = Field(..., min_length=1, max_length=20)
    account_type: str = Field("CORRENTE", pattern="^(CORRENTE|POUPANCA|SALARIO|PAGAMENTO)$")
    nickname: Optional[str] = Field(None, max_length=50)


class BeneficiaryResponse(BaseModel):
    id: str
    name: str
    cpf_cnpj: Optional[str] = None
    bank_name: str
    agency: Optional[str] = None
    account: str
    account_type: str
    nickname: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ── Transfer ────────────────────────────────────────────


class TransferSendRequest(BaseModel):
    beneficiary_id: Optional[str] = None
    receiver_name: str = Field(..., min_length=2)
    receiver_bank: str = Field(..., min_length=2)
    receiver_agency: Optional[str] = None
    receiver_account: str = Field(..., min_length=1)
    receiver_account_type: str = Field("CORRENTE", pattern="^(CORRENTE|POUPANCA|SALARIO|PAGAMENTO)$")
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=255)
    scheduled_date: Optional[str] = None


class TransferResponse(BaseModel):
    id: str
    receiver_name: str
    receiver_bank: str
    receiver_agency: Optional[str] = None
    receiver_account: str
    receiver_account_type: str
    amount: float
    description: Optional[str] = None
    status: str
    created_at: str
    beneficiary_id: Optional[str] = None

    class Config:
        from_attributes = True


class TransferListResponse(BaseModel):
    transfers: list[TransferResponse] = []
    total: int = 0


# ── Dashboard ───────────────────────────────────────────


class TransferDashboardResponse(BaseModel):
    balance: float = 0.0
    transfer_limit: float = 50000.0
    last_transfer_date: Optional[str] = None
    last_transfer_amount: Optional[float] = None
    total_transferred_month: float = 0.0
    scheduled_count: int = 0
