from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.usuarios import Usuario
from backend.schemas.login import LoginResponse
from backend.security import verificar_senha, criar_token


# Router padrão para rotas de login
router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/", response_model=LoginResponse)
def login_usuario(
    dados_login: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    
    # Recebe username e password no formato OAuth2 usado pelo Swagger.
    usuario = db.query(Usuario).filter(Usuario.usuario == dados_login.username).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # verifica se a senha é correta
    if not verificar_senha(dados_login.password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos"
        )
    
    # gera token para usuario
    token = criar_token({"sub":usuario.usuario})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.usuario
    }
