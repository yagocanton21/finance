from pydantic import BaseModel


# schema de criação de categoria
class CategoriaCreate(BaseModel):
    nome: str


# schema de resposta de categoria
class CategoriaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True