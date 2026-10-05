import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# cria motor de conexão com o banco de dados
def criar_engine():
    database_url = os.getenv("DATABASE_URL")
    return create_engine(database_url)


engine = criar_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# função para criar sessão com o banco de dados
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()