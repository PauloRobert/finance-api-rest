import pytest
from app.models.transaction import Transaction


class TestCreateTransaction:
    """Testes de criação de transação"""

    def test_create_income(self, client, auth_headers):
        response = client.post("/api/v1/transactions", json={
            "description": "Salário",
            "amount": 5000.00,
            "date": "2026-06-01T10:00:00",
            "type": "INCOME"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Salário"
        assert data["amount"] == 5000.00
        assert data["type"] == "INCOME"
        assert "id" in data

    def test_create_expense(self, client, auth_headers):
        response = client.post("/api/v1/transactions", json={
            "description": "Aluguel",
            "amount": 1500.00,
            "date": "2026-06-05T08:00:00",
            "type": "EXPENSE"
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "EXPENSE"

    def test_create_invalid_amount(self, client, auth_headers):
        response = client.post("/api/v1/transactions", json={
            "description": "Teste",
            "amount": -100,
            "date": "2026-06-01T10:00:00",
            "type": "INCOME"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_missing_description(self, client, auth_headers):
        response = client.post("/api/v1/transactions", json={
            "amount": 100,
            "date": "2026-06-01T10:00:00",
            "type": "INCOME"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_invalid_type(self, client, auth_headers):
        response = client.post("/api/v1/transactions", json={
            "description": "Teste",
            "amount": 100,
            "date": "2026-06-01T10:00:00",
            "type": "INVALID"
        }, headers=auth_headers)
        assert response.status_code == 422

    def test_create_without_auth(self, client):
        response = client.post("/api/v1/transactions", json={
            "description": "Salário",
            "amount": 5000.00,
            "date": "2026-06-01T10:00:00",
            "type": "INCOME"
        })
        assert response.status_code == 403


class TestListTransactions:
    """Testes de listagem de transações"""

    def test_list_empty(self, client, auth_headers):
        response = client.get("/api/v1/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["transactions"] == []
        assert data["total"] == 0

    def test_list_with_transactions(self, client, auth_headers, db_session, test_user):
        # Criar transações diretamente no banco
        t1 = Transaction(
            description="Salário", amount=5000, date="2026-06-01",
            type="INCOME", user_id=test_user.id
        )
        t2 = Transaction(
            description="Aluguel", amount=1500, date="2026-06-05",
            type="EXPENSE", user_id=test_user.id
        )
        db_session.add_all([t1, t2])
        db_session.commit()

        response = client.get("/api/v1/transactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_only_own_transactions(self, client, auth_headers, db_session, test_user):
        # Transação de outro usuário
        other_tx = Transaction(
            description="Outro", amount=999, date="2026-06-01",
            type="INCOME", user_id="other-user-id"
        )
        db_session.add(other_tx)
        db_session.commit()

        response = client.get("/api/v1/transactions", headers=auth_headers)
        data = response.json()
        assert data["total"] == 0

    def test_list_without_auth(self, client):
        response = client.get("/api/v1/transactions")
        assert response.status_code == 403


class TestGetTransaction:
    """Testes de busca de transação por ID"""

    def test_get_existing(self, client, auth_headers, db_session, test_user):
        tx = Transaction(
            id="tx-123", description="Teste", amount=100,
            date="2026-06-01", type="INCOME", user_id=test_user.id
        )
        db_session.add(tx)
        db_session.commit()

        response = client.get("/api/v1/transactions/tx-123", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == "tx-123"

    def test_get_nonexistent(self, client, auth_headers):
        response = client.get("/api/v1/transactions/fake-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_other_user_transaction(self, client, auth_headers, db_session):
        tx = Transaction(
            id="tx-other", description="Outro", amount=100,
            date="2026-06-01", type="INCOME", user_id="another-user"
        )
        db_session.add(tx)
        db_session.commit()

        response = client.get("/api/v1/transactions/tx-other", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateTransaction:
    """Testes de atualização de transação"""

    def test_update_description(self, client, auth_headers, db_session, test_user):
        tx = Transaction(
            id="tx-upd", description="Original", amount=100,
            date="2026-06-01", type="INCOME", user_id=test_user.id
        )
        db_session.add(tx)
        db_session.commit()

        response = client.put("/api/v1/transactions/tx-upd", json={
            "description": "Atualizado"
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["description"] == "Atualizado"
        assert response.json()["amount"] == 100  # não mudou

    def test_update_amount(self, client, auth_headers, db_session, test_user):
        tx = Transaction(
            id="tx-upd2", description="Teste", amount=100,
            date="2026-06-01", type="INCOME", user_id=test_user.id
        )
        db_session.add(tx)
        db_session.commit()

        response = client.put("/api/v1/transactions/tx-upd2", json={
            "amount": 250.50
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["amount"] == 250.50

    def test_update_nonexistent(self, client, auth_headers):
        response = client.put("/api/v1/transactions/fake", json={
            "description": "Nope"
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_update_other_user_transaction(self, client, auth_headers, db_session):
        tx = Transaction(
            id="tx-other-upd", description="Outro", amount=100,
            date="2026-06-01", type="INCOME", user_id="other-user"
        )
        db_session.add(tx)
        db_session.commit()

        response = client.put("/api/v1/transactions/tx-other-upd", json={
            "description": "Hack"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteTransaction:
    """Testes de exclusão de transação"""

    def test_delete_success(self, client, auth_headers, db_session, test_user):
        tx = Transaction(
            id="tx-del", description="Deletar", amount=50,
            date="2026-06-01", type="EXPENSE", user_id=test_user.id
        )
        db_session.add(tx)
        db_session.commit()

        response = client.delete("/api/v1/transactions/tx-del", headers=auth_headers)
        assert response.status_code == 204

        # Confirmar que foi deletado
        response = client.get("/api/v1/transactions/tx-del", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        response = client.delete("/api/v1/transactions/fake", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_other_user_transaction(self, client, auth_headers, db_session):
        tx = Transaction(
            id="tx-other-del", description="Outro", amount=100,
            date="2026-06-01", type="INCOME", user_id="other-user"
        )
        db_session.add(tx)
        db_session.commit()

        response = client.delete("/api/v1/transactions/tx-other-del", headers=auth_headers)
        assert response.status_code == 404
