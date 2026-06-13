from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

# Configuração do engine com pool para performance
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy"""

    pass


def get_db():
    """Dependency injection para sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
