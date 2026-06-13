"""
Script de seed: insere 1 usuário de teste e 50 transações financeiras realistas.
Execução: python scripts/seed_data.py
"""

import sys
import uuid
from pathlib import Path

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.services.auth_service import hash_password

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

# --- Dados do usuário de teste ---
TEST_USER = {
    "id": str(uuid.uuid4()),
    "username": "paulo",
    "password": "senha123456",
}

# --- 50 transações financeiras realistas (variadas ao longo de 6 meses) ---
TRANSACTIONS = [
    # Janeiro 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-01-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-01-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta de energia elétrica", "amount": 189.50, "date": "2026-01-12T10:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta de água e esgoto", "amount": 95.30, "date": "2026-01-12T10:30:00", "type": TransactionType.EXPENSE},
    {"description": "Internet fibra 500Mbps", "amount": 129.90, "date": "2026-01-15T11:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 487.60, "date": "2026-01-18T14:00:00", "type": TransactionType.EXPENSE},
    {"description": "Freelance desenvolvimento web", "amount": 3200.00, "date": "2026-01-20T16:00:00", "type": TransactionType.INCOME},
    {"description": "Plano de saúde", "amount": 450.00, "date": "2026-01-22T08:00:00", "type": TransactionType.EXPENSE},
    {"description": "Academia mensalidade", "amount": 119.90, "date": "2026-01-25T07:00:00", "type": TransactionType.EXPENSE},
    # Fevereiro 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-02-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-02-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 523.40, "date": "2026-02-08T15:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 412.80, "date": "2026-02-15T14:30:00", "type": TransactionType.EXPENSE},
    {"description": "Gasolina veículo", "amount": 280.00, "date": "2026-02-11T18:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta de energia elétrica", "amount": 210.75, "date": "2026-02-12T10:00:00", "type": TransactionType.EXPENSE},
    {"description": "Dividendos ações ITUB4", "amount": 342.50, "date": "2026-02-14T09:00:00", "type": TransactionType.INCOME},
    {"description": "Jantar restaurante", "amount": 178.90, "date": "2026-02-14T21:00:00", "type": TransactionType.EXPENSE},
    {"description": "Seguro automóvel parcela", "amount": 385.00, "date": "2026-02-20T08:00:00", "type": TransactionType.EXPENSE},
    # Março 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-03-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-03-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "IPTU parcela 3/10", "amount": 320.00, "date": "2026-03-08T08:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 498.20, "date": "2026-03-12T14:00:00", "type": TransactionType.EXPENSE},
    {"description": "Manutenção veículo - revisão", "amount": 890.00, "date": "2026-03-15T10:00:00", "type": TransactionType.EXPENSE},
    {"description": "Venda item usado OLX", "amount": 450.00, "date": "2026-03-17T16:00:00", "type": TransactionType.INCOME},
    {"description": "Assinatura streaming (Netflix + Spotify)", "amount": 75.80, "date": "2026-03-18T08:00:00", "type": TransactionType.EXPENSE},
    {"description": "Farmácia medicamentos", "amount": 132.40, "date": "2026-03-20T12:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta telefone celular", "amount": 69.90, "date": "2026-03-22T09:00:00", "type": TransactionType.EXPENSE},
    # Abril 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-04-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Bônus trimestral empresa", "amount": 4250.00, "date": "2026-04-05T08:30:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-04-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 551.30, "date": "2026-04-06T15:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 389.70, "date": "2026-04-13T14:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta de gás encanado", "amount": 67.40, "date": "2026-04-14T10:00:00", "type": TransactionType.EXPENSE},
    {"description": "Curso online Udemy", "amount": 49.90, "date": "2026-04-16T20:00:00", "type": TransactionType.EXPENSE},
    {"description": "Rendimento CDB Nubank", "amount": 187.30, "date": "2026-04-18T09:00:00", "type": TransactionType.INCOME},
    {"description": "Presente aniversário (compra)", "amount": 250.00, "date": "2026-04-20T17:00:00", "type": TransactionType.EXPENSE},
    {"description": "Estacionamento shopping", "amount": 22.00, "date": "2026-04-20T19:00:00", "type": TransactionType.EXPENSE},
    # Maio 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-05-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-05-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "Conta de energia elétrica", "amount": 175.20, "date": "2026-05-12T10:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado quinzenal", "amount": 620.50, "date": "2026-05-14T14:00:00", "type": TransactionType.EXPENSE},
    {"description": "Consulta médica particular", "amount": 350.00, "date": "2026-05-16T15:00:00", "type": TransactionType.EXPENSE},
    {"description": "Gasolina veículo", "amount": 295.00, "date": "2026-05-18T18:30:00", "type": TransactionType.EXPENSE},
    {"description": "Freelance consultoria TI", "amount": 2800.00, "date": "2026-05-20T10:00:00", "type": TransactionType.INCOME},
    {"description": "Condomínio", "amount": 580.00, "date": "2026-05-22T08:00:00", "type": TransactionType.EXPENSE},
    # Junho 2026
    {"description": "Salário mensal", "amount": 8500.00, "date": "2026-06-05T08:00:00", "type": TransactionType.INCOME},
    {"description": "Aluguel apartamento", "amount": 2200.00, "date": "2026-06-10T09:00:00", "type": TransactionType.EXPENSE},
    {"description": "Supermercado semanal", "amount": 475.90, "date": "2026-06-07T14:00:00", "type": TransactionType.EXPENSE},
    {"description": "Uber/99 corridas do mês", "amount": 156.80, "date": "2026-06-09T22:00:00", "type": TransactionType.EXPENSE},
    {"description": "Dividendos FIIs", "amount": 520.00, "date": "2026-06-12T09:00:00", "type": TransactionType.INCOME},
]


def seed():
    db = SessionLocal()
    try:
        # Verificar se usuário já existe
        existing_user = db.query(User).filter(User.username == TEST_USER["username"]).first()
        if existing_user:
            print(f"Usuário '{TEST_USER['username']}' já existe (id={existing_user.id}). Usando existente.")
            user_id = existing_user.id
        else:
            user = User(
                id=TEST_USER["id"],
                username=TEST_USER["username"],
                hashed_password=hash_password(TEST_USER["password"]),
                is_active=True,
            )
            db.add(user)
            db.commit()
            user_id = user.id
            print(f"Usuário criado: {TEST_USER['username']} (id={user_id})")

        # Inserir transações
        count = 0
        for tx_data in TRANSACTIONS:
            transaction = Transaction(
                id=str(uuid.uuid4()),
                description=tx_data["description"],
                amount=tx_data["amount"],
                date=tx_data["date"],
                type=tx_data["type"],
                user_id=user_id,
            )
            db.add(transaction)
            count += 1

        db.commit()
        print(f"\n{count} transações inseridas com sucesso!")
        print(f"\nCredenciais de acesso:")
        print(f"  Username: {TEST_USER['username']}")
        print(f"  Password: {TEST_USER['password']}")

        # Resumo
        incomes = sum(t["amount"] for t in TRANSACTIONS if t["type"] == TransactionType.INCOME)
        expenses = sum(t["amount"] for t in TRANSACTIONS if t["type"] == TransactionType.EXPENSE)
        print(f"\nResumo financeiro:")
        print(f"  Total receitas:  R$ {incomes:,.2f}")
        print(f"  Total despesas:  R$ {expenses:,.2f}")
        print(f"  Saldo:           R$ {incomes - expenses:,.2f}")

    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
