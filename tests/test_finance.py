"""Tests for finance module models and basic validation."""
import pytest
from app.models.finance import (
    CardStatus, CardType, DepositStatus, DepositType,
    InvestmentStatus, InvestmentType, PaymentStatus, PaymentType,
)


class TestEnums:
    def test_deposit_types(self):
        assert DepositType.BOLETO.value == "BOLETO"
        assert DepositType.PIX.value == "PIX"
        assert DepositType.TED.value == "TED"

    def test_deposit_status(self):
        assert DepositStatus.COMPLETED.value == "COMPLETED"
        assert DepositStatus.PENDING.value == "PENDING"

    def test_payment_types(self):
        assert PaymentType.BOLETO.value == "BOLETO"
        assert PaymentType.UTILITY.value == "UTILITY"
        assert PaymentType.TAX.value == "TAX"

    def test_payment_status(self):
        assert PaymentStatus.COMPLETED.value == "COMPLETED"
        assert PaymentStatus.SCHEDULED.value == "SCHEDULED"

    def test_card_types(self):
        assert CardType.DEBIT.value == "DEBIT"
        assert CardType.CREDIT.value == "CREDIT"
        assert CardType.VIRTUAL.value == "VIRTUAL"

    def test_card_status(self):
        assert CardStatus.ACTIVE.value == "ACTIVE"
        assert CardStatus.BLOCKED.value == "BLOCKED"
        assert CardStatus.CANCELLED.value == "CANCELLED"

    def test_investment_types(self):
        assert InvestmentType.CDB.value == "CDB"
        assert InvestmentType.TESOURO.value == "TESOURO"
        assert InvestmentType.ACAO.value == "ACAO"

    def test_investment_status(self):
        assert InvestmentStatus.ACTIVE.value == "ACTIVE"
        assert InvestmentStatus.REDEEMED.value == "REDEEMED"


class TestSchemaValidation:
    def test_deposit_request_valid(self):
        from app.schemas.finance import DepositRequest
        req = DepositRequest(amount=100.0, deposit_type="PIX")
        assert req.amount == 100.0

    def test_deposit_request_invalid_amount(self):
        from app.schemas.finance import DepositRequest
        with pytest.raises(Exception):
            DepositRequest(amount=-10.0, deposit_type="PIX")

    def test_payment_request_valid(self):
        from app.schemas.finance import PaymentRequest
        req = PaymentRequest(payee_name="CEMIG", amount=150.0)
        assert req.payee_name == "CEMIG"

    def test_card_create_valid(self):
        from app.schemas.finance import CardCreateRequest
        req = CardCreateRequest(card_name="Meu Cartão", card_type="CREDIT", credit_limit=5000.0)
        assert req.credit_limit == 5000.0

    def test_investment_create_valid(self):
        from app.schemas.finance import InvestmentCreateRequest
        req = InvestmentCreateRequest(name="CDB 120%", investment_type="CDB", amount=1000.0)
        assert req.investment_type == "CDB"

    def test_investment_dashboard_defaults(self):
        from app.schemas.finance import InvestmentDashboardResponse
        dash = InvestmentDashboardResponse()
        assert dash.total_invested == 0.0
        assert dash.profit_percentage == 0.0
