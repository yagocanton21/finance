import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.usuarios import Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "21f582ec6dfebf7833aaaf8a8fa69b7b72161d7c12b4045a3f25c5c7f6ea35f3")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# gera criptografia para a senha
def hash_senha(senha: str, rounds: int = 12) -> str:
    """Gera um hash seguro a partir de uma senha em texto puro e retorna como string."""
    salt = bcrypt.gensalt(rounds=rounds)
    hashed_bytes = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

# verifica se a senha é igual ao hash
def verificar_senha(senha_plana: str, hash_salvo: str) -> bool:
    """Compara uma senha informada com o hash salvo no banco de dados."""
    return bcrypt.checkpw(
        senha_plana.encode('utf-8'),
        hash_salvo.encode('utf-8')
    )

# cria um token jwt para o usuário
def criar_token(dados: dict) -> str:
    payload = dados.copy()
    
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiracao})
    
    # Codifica e assina o token
    token_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

# obtém o usuário autenticado a partir do token jwt
def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nome_usuario: str | None = payload.get("sub")
        if nome_usuario is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.usuario == nome_usuario).first()
    if usuario is None:
        raise credentials_exception

    return usuario


