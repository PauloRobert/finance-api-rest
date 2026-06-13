from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env"""

    database_url: str = "sqlite:///./finance.db"
    secret_key: str = "finance-app-dev-secret-key-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações"""
    return Settings()
