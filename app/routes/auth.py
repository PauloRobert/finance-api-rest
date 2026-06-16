from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.finance import Card, CardType
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_user_by_username,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário no sistema"""
    # Verificar se username já existe
    existing = get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username já está em uso"
        )

    # Criar usuário
    new_user = User(
        username=user_data.username, hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Criar cartões padrão para o novo usuário
    import uuid
    import hashlib

    last_four_debit = f"{int(hashlib.sha256(new_user.id.encode()).hexdigest(), 16) % 10000:04d}"
    last_four_credit = f"{(int(hashlib.sha256((new_user.id + 'cc').encode()).hexdigest(), 16) % 10000):04d}"

    debit_card = Card(
        user_id=new_user.id,
        card_name=f"Débito IF Bank",
        last_four=last_four_debit,
        card_type=CardType.DEBIT,
        credit_limit=0.0,
        available_limit=0.0,
    )
    credit_card = Card(
        user_id=new_user.id,
        card_name=f"Crédito IF Bank Gold",
        last_four=last_four_credit,
        card_type=CardType.CREDIT,
        credit_limit=5000.0,
        available_limit=5000.0,
        due_day="15",
    )
    db.add(debit_card)
    db.add(credit_card)
    db.commit()

    return new_user


@router.post(
    "/login", response_model=TokenResponse, summary="Autenticar e obter token JWT"
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
