import pytest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    """Testes de hashing de senha"""

    def test_hash_password_returns_hash(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        h1 = hash_password("samepass")
        h2 = hash_password("samepass")
        assert h1 != h2  # bcrypt gera salt diferente

    def test_verify_password_correct(self):
        hashed = hash_password("correctpassword")
        assert verify_password("correctpassword", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    """Testes de criação e decodificação de tokens JWT"""

    def test_create_and_decode_token(self):
        token = create_access_token(data={"sub": "user-123"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        result = decode_token("invalid.token.here")
        assert result is None

    def test_decode_tampered_token(self):
        token = create_access_token(data={"sub": "user-123"})
        # Modificar payload
        tampered = token[:-5] + "XXXXX"
        result = decode_token(tampered)
        assert result is None

    def test_token_contains_expiration(self):
        token = create_access_token(data={"sub": "user-456"})
        payload = decode_token(token)
        assert "exp" in payload
