from datetime import datetime
from pydantic import BaseModel

# schema de criação de usuário
class UsuarioCreate(BaseModel):
    usuario: str
    senha: str

# schema de resposta de usuário
class UsuarioResponse(BaseModel):
    id: int
    usuario: str
    criado_em: datetime

    class Config:
        from_attributes = True