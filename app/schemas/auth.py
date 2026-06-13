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

