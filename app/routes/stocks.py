from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/stocks", tags=["Ações"])


class StockQuote(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: str
    market_cap: str
    sector: str


# Dados simulados de ações brasileiras (pregão)
STOCK_DATA = [
    StockQuote(symbol="PETR4", name="Petrobras PN", price=38.72, change=0.85, change_percent=2.24, volume="45.2M", market_cap="R$ 502B", sector="Petróleo"),
    StockQuote(symbol="VALE3", name="Vale ON", price=61.45, change=-1.20, change_percent=-1.91, volume="32.8M", market_cap="R$ 272B", sector="Mineração"),
    StockQuote(symbol="ITUB4", name="Itaú Unibanco PN", price=34.18, change=0.42, change_percent=1.24, volume="28.5M", market_cap="R$ 332B", sector="Financeiro"),
    StockQuote(symbol="BBDC4", name="Bradesco PN", price=15.23, change=-0.18, change_percent=-1.17, volume="22.1M", market_cap="R$ 161B", sector="Financeiro"),
    StockQuote(symbol="ABEV3", name="Ambev ON", price=13.85, change=0.12, change_percent=0.87, volume="18.9M", market_cap="R$ 218B", sector="Bebidas"),
    StockQuote(symbol="WEGE3", name="WEG ON", price=42.30, change=1.55, change_percent=3.80, volume="8.7M", market_cap="R$ 177B", sector="Industrial"),
    StockQuote(symbol="BBAS3", name="Banco do Brasil ON", price=28.90, change=0.35, change_percent=1.23, volume="15.3M", market_cap="R$ 165B", sector="Financeiro"),
    StockQuote(symbol="MGLU3", name="Magazine Luiza ON", price=12.45, change=-0.68, change_percent=-5.18, volume="42.6M", market_cap="R$ 8.5B", sector="Varejo"),
    StockQuote(symbol="RENT3", name="Localiza ON", price=58.10, change=2.30, change_percent=4.12, volume="6.2M", market_cap="R$ 58B", sector="Locação"),
    StockQuote(symbol="SUZB3", name="Suzano ON", price=52.75, change=-0.90, change_percent=-1.68, volume="9.1M", market_cap="R$ 68B", sector="Celulose"),
    StockQuote(symbol="HAPV3", name="Hapvida ON", price=4.32, change=0.08, change_percent=1.89, volume="35.4M", market_cap="R$ 32B", sector="Saúde"),
    StockQuote(symbol="B3SA3", name="B3 ON", price=12.80, change=0.22, change_percent=1.75, volume="20.7M", market_cap="R$ 73B", sector="Financeiro"),
]


class StockListResponse(BaseModel):
    stocks: list[StockQuote] = []
    ibovespa: float = 128450.0
    ibovespa_change: float = 1.35


@router.get("/", response_model=StockListResponse)
def get_stocks(current_user: User = Depends(get_current_user)):
    return StockListResponse(stocks=STOCK_DATA)
