from pydantic import BaseModel

# schema de criação de login
class LoginCreate(BaseModel):
    usuario: str
    senha: str

# schema de resposta de login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: str