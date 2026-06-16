from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema para registro de usuário"""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema para login"""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema de resposta do token JWT"""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema de resposta do usuário"""

    id: str
    username: str
    is_active: bool

    class Config:
        from_attributes = True


# ── Profile ─────────────────────────────────────────────


class ProfileResponse(BaseModel):
    """Resposta do perfil do usuário"""

    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Schema para atualização do perfil"""

    display_name: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


# ── Security ────────────────────────────────────────────


class SecurityResponse(BaseModel):
    """Resposta das configurações de segurança"""

    two_factor_enabled: bool = False
    biometric_enabled: bool = False
    login_notification_enabled: bool = True
    last_password_change: Optional[str] = None

    class Config:
        from_attributes = True


class SecurityUpdate(BaseModel):
    """Schema para atualização das configurações de segurança"""

    two_factor_enabled: Optional[bool] = None
    biometric_enabled: Optional[bool] = None
    login_notification_enabled: Optional[bool] = None


class PasswordChange(BaseModel):
    """Schema para troca de senha"""

    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)


# ── Privacy ─────────────────────────────────────────────


class PrivacyResponse(BaseModel):
    """Resposta das configurações de privacidade"""

    share_usage_data: bool = False
    show_balance_on_home: bool = True
    transaction_notifications: bool = True
    marketing_emails: bool = False

    class Config:
        from_attributes = True


class PrivacyUpdate(BaseModel):
    """Schema para atualização das configurações de privacidade"""

    share_usage_data: Optional[bool] = None
    show_balance_on_home: Optional[bool] = None
    transaction_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
