from typing import Optional

from pydantic import BaseModel, Field


# ── Pix Keys ────────────────────────────────────────────


class PixKeyCreate(BaseModel):
    key_type: str = Field(..., pattern="^(CPF|CNPJ|EMAIL|PHONE|RANDOM)$")
    key_value: str = Field(..., min_length=1, max_length=255)


class PixKeyResponse(BaseModel):
    id: str
    key_type: str
    key_value: str
    is_active: bool

    class Config:
        from_attributes = True


# ── Pix Transfer ────────────────────────────────────────


class PixKeyLookupResponse(BaseModel):
    key_value: str
    owner_name: str
    bank: str = "IF Bank"


class PixSendRequest(BaseModel):
    receiver_key: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=255)
    scheduled_date: Optional[str] = None


class PixTransferResponse(BaseModel):
    id: str
    receiver_key: str
    receiver_name: Optional[str] = None
    receiver_bank: Optional[str] = None
    amount: float
    description: Optional[str] = None
    status: str
    created_at: str
    is_favorite: bool = False

    class Config:
        from_attributes = True


class PixTransferListResponse(BaseModel):
    transfers: list[PixTransferResponse] = []
    total: int = 0


# ── Pix Dashboard ───────────────────────────────────────


class PixDashboardResponse(BaseModel):
    balance: float = 0.0
    daily_limit: float = 20000.0
    daily_used: float = 0.0
    pix_active: bool = True
    total_sent_month: float = 0.0
    total_received_month: float = 0.0
    keys_count: int = 0


# ── Favorites ───────────────────────────────────────────


class PixFavoriteResponse(BaseModel):
    receiver_key: str
    receiver_name: Optional[str] = None
    receiver_bank: Optional[str] = None
    last_amount: float = 0.0
