from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User

settings = get_settings()


def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt diretamente"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha confere com o hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    """Cria token JWT com expiração configurável"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    """Decodifica e valida token JWT"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Autentica usuário por username e senha"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()
