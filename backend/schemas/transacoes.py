from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# schema de criação de transação
class TransacaoCreate(BaseModel):
    descricao: str
    tipo: str  # ex: "RECEITA" ou "DESPESA"
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    categoria_id: int | None = None

# schema de resposta de transação
class TransacaoResponse(BaseModel):
    id: int
    usuario_id: int
    descricao: str
    tipo: str
    valor: Decimal
    categoria_id: int | None = None
    criado_em: datetime

    class Config:
        from_attributes = True
