# Finance App - API REST

API REST para o aplicativo FinanceApp, construída com FastAPI.

## Tecnologias

- **FastAPI** — Framework web assíncrono de alta performance
- **SQLAlchemy** — ORM para acesso ao banco de dados
- **PostgreSQL** — Banco de dados (produção)
- **SQLite** — Banco de dados (desenvolvimento local)
- **JWT (python-jose)** — Autenticação via token
- **bcrypt** — Hash de senhas
- **Pydantic** — Validação de dados

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração do Banco de Dados

### Desenvolvimento local (SQLite)
Sem configuração adicional — o padrão é SQLite.

### Produção (PostgreSQL)
Defina a variável de ambiente `DATABASE_URL` com a connection string do PostgreSQL:

```bash
DATABASE_URL=postgresql://usuario:senha@host:5432/finance_db
```

No DigitalOcean App Platform, adicione essa variável nas configurações do app apontando para o Managed Database.

## Execução

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentação

Após iniciar o servidor:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Registrar usuário |
| POST | `/api/v1/auth/login` | Login (retorna JWT) |

### Transações (requer token)
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/transactions` | Listar transações |
| GET | `/api/v1/transactions/{id}` | Buscar por ID |
| POST | `/api/v1/transactions` | Criar transação |
| PUT | `/api/v1/transactions/{id}` | Atualizar transação |
| DELETE | `/api/v1/transactions/{id}` | Excluir transação |

## Estrutura

```
finance-api-rest/
├── app/
│   ├── main.py          # Ponto de entrada
│   ├── config.py        # Configurações (.env)
│   ├── database.py      # Conexão SQLAlchemy
│   ├── models/          # Modelos do banco
│   ├── schemas/         # Schemas Pydantic
│   ├── routes/          # Rotas/Controllers
│   ├── services/        # Lógica de negócio
│   └── middleware/      # Autenticação JWT
├── requirements.txt
├── .env
└── README.md
```

