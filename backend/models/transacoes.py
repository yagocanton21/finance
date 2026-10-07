from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    descricao = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    criado_em = Column(DateTime, default=datetime.now)
    atualizado_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    data_vencimento = Column(Date)
    pago = Column(Boolean, default=False)
    parcela_atual = Column(Integer)
    total_parcelas = Column(Integer)
    grupo_id = Column(String)

    usuario = relationship("Usuario")
    categoria = relationship("Categoria")