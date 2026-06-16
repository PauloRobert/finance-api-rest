from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserPrivacy, UserProfile, UserSecurity
from app.schemas.auth import (
    PasswordChange,
    PrivacyResponse,
    PrivacyUpdate,
    ProfileResponse,
    ProfileUpdate,
    SecurityResponse,
    SecurityUpdate,
)
from app.services.auth_service import hash_password, verify_password

router = APIRouter(prefix="/user", tags=["Usuário"])


# ── Helpers ─────────────────────────────────────────────


def _get_or_create_profile(db: Session, user: User) -> UserProfile:
    """Retorna o perfil existente ou cria um novo."""
    if user.profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    return user.profile


def _get_or_create_security(db: Session, user: User) -> UserSecurity:
    if user.security is None:
        security = UserSecurity(user_id=user.id)
        db.add(security)
        db.commit()
        db.refresh(security)
        return security
    return user.security


def _get_or_create_privacy(db: Session, user: User) -> UserPrivacy:
    if user.privacy is None:
        privacy = UserPrivacy(user_id=user.id)
        db.add(privacy)
        db.commit()
        db.refresh(privacy)
        return privacy
    return user.privacy


# ── Profile ─────────────────────────────────────────────


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Obter perfil do usuário",
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(db, current_user)
    return ProfileResponse(
        username=current_user.username,
        display_name=profile.display_name,
        email=profile.email,
        phone=profile.phone,
    )


@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Atualizar perfil do usuário",
)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_or_create_profile(db, current_user)

    if data.display_name is not None:
        profile.display_name = data.display_name.strip()
    if data.email is not None:
        profile.email = data.email.strip().lower()
    if data.phone is not None:
        profile.phone = data.phone.strip()

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        username=current_user.username,
        display_name=profile.display_name,
        email=profile.email,
        phone=profile.phone,
    )


# ── Security ────────────────────────────────────────────


@router.get(
    "/security",
    response_model=SecurityResponse,
    summary="Obter configurações de segurança",
)
def get_security(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = _get_or_create_security(db, current_user)
    return SecurityResponse(
        two_factor_enabled=security.two_factor_enabled,
        biometric_enabled=security.biometric_enabled,
        login_notification_enabled=security.login_notification_enabled,
        last_password_change=(
            security.last_password_change.isoformat()
            if security.last_password_change
            else None
        ),
    )


@router.put(
    "/security",
    response_model=SecurityResponse,
    summary="Atualizar configurações de segurança",
)
def update_security(
    data: SecurityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = _get_or_create_security(db, current_user)

    if data.two_factor_enabled is not None:
        security.two_factor_enabled = data.two_factor_enabled
    if data.biometric_enabled is not None:
        security.biometric_enabled = data.biometric_enabled
    if data.login_notification_enabled is not None:
        security.login_notification_enabled = data.login_notification_enabled

    db.commit()
    db.refresh(security)

    return SecurityResponse(
        two_factor_enabled=security.two_factor_enabled,
        biometric_enabled=security.biometric_enabled,
        login_notification_enabled=security.login_notification_enabled,
        last_password_change=(
            security.last_password_change.isoformat()
            if security.last_password_change
            else None
        ),
    )


@router.post(
    "/security/change-password",
    status_code=status.HTTP_200_OK,
    summary="Alterar senha do usuário",
)
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verificar senha atual
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )

    # Impedir que a nova senha seja igual à atual
    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da atual",
        )

    current_user.hashed_password = hash_password(data.new_password)

    security = _get_or_create_security(db, current_user)
    security.last_password_change = datetime.now(timezone.utc)

    db.commit()
    return {"message": "Senha alterada com sucesso"}


# ── Privacy ─────────────────────────────────────────────


@router.get(
    "/privacy",
    response_model=PrivacyResponse,
    summary="Obter configurações de privacidade",
)
def get_privacy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    privacy = _get_or_create_privacy(db, current_user)
    return PrivacyResponse(
        share_usage_data=privacy.share_usage_data,
        show_balance_on_home=privacy.show_balance_on_home,
        transaction_notifications=privacy.transaction_notifications,
        marketing_emails=privacy.marketing_emails,
    )


@router.put(
    "/privacy",
    response_model=PrivacyResponse,
    summary="Atualizar configurações de privacidade",
)
def update_privacy(
    data: PrivacyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    privacy = _get_or_create_privacy(db, current_user)

    if data.share_usage_data is not None:
        privacy.share_usage_data = data.share_usage_data
    if data.show_balance_on_home is not None:
        privacy.show_balance_on_home = data.show_balance_on_home
    if data.transaction_notifications is not None:
        privacy.transaction_notifications = data.transaction_notifications
    if data.marketing_emails is not None:
        privacy.marketing_emails = data.marketing_emails

    db.commit()
    db.refresh(privacy)

    return PrivacyResponse(
        share_usage_data=privacy.share_usage_data,
        show_balance_on_home=privacy.show_balance_on_home,
        transaction_notifications=privacy.transaction_notifications,
        marketing_emails=privacy.marketing_emails,
    )
