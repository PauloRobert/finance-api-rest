from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import auth, transaction

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Instância da aplicação FastAPI
app = FastAPI(
    title="Finance App API",
    description="API REST para gerenciamento de transações financeiras",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração CORS para permitir acesso do app Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(auth.router, prefix="/api/v1")
app.include_router(transaction.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return {"status": "online", "version": "1.0.0"}
