import pytest


class TestRegister:
    """Testes de registro de usuário"""

    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "newuser", "password": "securepass123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_username(self, client, test_user):
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "password": "anotherpass"},
        )
        assert response.status_code == 409
        assert "já está em uso" in response.json()["detail"]

    def test_register_short_username(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "ab", "password": "securepass123"},
        )
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post(
            "/api/v1/auth/register", json={"username": "validuser", "password": "12345"}
        )
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


class TestLogin:
    """Testes de login"""

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "inválidas" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "ghostuser", "password": "somepass123"},
        )
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
