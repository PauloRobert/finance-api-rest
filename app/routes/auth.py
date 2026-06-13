from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_user_by_username,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário no sistema"""
    # Verificar se username já existe
    existing = get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username já está em uso"
        )

    # Criar usuário
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar e obter token JWT"
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Autentica o usuário e retorna um token JWT"""
    user = authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})

    return TokenResponse(access_token=access_token)

