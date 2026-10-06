from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# schema de criação de transação
class TransacaoCreate(BaseModel):
    descricao: str
    tipo: str  # ex: "RECEITA" ou "DESPESA"
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    categoria_id: int | None = None
    data_vencimento: date | None = None
    pago: bool = False
    total_parcelas: int = Field(default=1, ge=1)  # se > 1, gera o parcelamento automático


# schema de atualização de transação
class TransacaoUpdate(BaseModel):
    descricao: str | None = None
    tipo: str | None = None
    valor: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    categoria_id: int | None = None
    data_vencimento: date | None = None
    pago: bool | None = None


# schema de resposta de transação
class TransacaoResponse(BaseModel):
    id: int
    usuario_id: int
    categoria_id: int | None = None
    descricao: str
    tipo: str
    valor: Decimal
    data_vencimento: date | None = None
    pago: bool
    parcela_atual: int | None = None
    total_parcelas: int | None = None
    grupo_id: str | None = None
    criado_em: datetime

    class Config:
        from_attributes = True
