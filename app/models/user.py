import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Modelo de usuário para autenticação"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
