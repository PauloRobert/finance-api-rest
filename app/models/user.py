import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
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

    # Relacionamentos
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    security = relationship("UserSecurity", back_populates="user", uselist=False, cascade="all, delete-orphan")
    privacy = relationship("UserPrivacy", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    """Perfil do usuário — dados pessoais editáveis"""

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class UserSecurity(Base):
    """Configurações de segurança do usuário"""

    __tablename__ = "user_security"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    two_factor_enabled = Column(Boolean, default=False)
    biometric_enabled = Column(Boolean, default=False)
    login_notification_enabled = Column(Boolean, default=True)
    last_password_change = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="security")


class UserPrivacy(Base):
    """Configurações de privacidade do usuário"""

    __tablename__ = "user_privacy"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    share_usage_data = Column(Boolean, default=False)
    show_balance_on_home = Column(Boolean, default=True)
    transaction_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="privacy")
