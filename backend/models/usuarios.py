from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from backend.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )