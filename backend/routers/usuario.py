from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.usuarios import Usuario
from backend.schemas.usuario import UsuarioCreate, UsuarioResponse
from backend.security import hash_senha

router = APIRouter(
    prefix="/usuario",
    tags=["usuario"]
)

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados_usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Verifica se já existe um usuário com esse login
    usuario_existente = db.query(Usuario).filter(Usuario.usuario == dados_usuario.usuario).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Usuário já existente")

    # 2. Cria o novo usuário com a senha criptografada
    novo_usuario = Usuario(
        usuario=dados_usuario.usuario,
        senha=hash_senha(dados_usuario.senha)
    )

    # 3. Salva no banco de dados
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # 4. Retorna o usuário criado
    return novo_usuario

# rota para listar todos os usuarios
@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    
    #1. busca todos os usuarios no banco de dados
    usuarios = db.query(Usuario).all()
    return usuarios
    
# Rota para listar um usuario especifico
@router.get("/{id}", response_model=UsuarioResponse)
def listar_usuario_por_id(id: int, db: Session = Depends(get_db)):
    
    # busca o id do usuario e verifica se ele existe
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    
    # se o usuario nao existir, retorna um erro 404
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    return usuario

# rota para atualizar um usuario
@router.put("/{id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def atualizar_usuario(id: int, dados_usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Busca o usuário que será alterado
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    # 2. Verifica se o novo nome de usuário já está sendo usado por OUTRA pessoa
    usuario_existente = db.query(Usuario).filter(
        Usuario.usuario == dados_usuario.usuario,
        Usuario.id != id
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este nome de usuário já está em uso por outra conta."
        )
    # 3. Atualiza os campos com os novos dados
    usuario.usuario = dados_usuario.usuario
    usuario.senha = hash_senha(dados_usuario.senha)
    # 4. Salva as mudanças no PostgreSQL
    db.commit()
    db.refresh(usuario)
    # 5. Retorna o usuário atualizado
    return usuario
   
# rota para deletar um usuario
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def deletar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    db.delete(usuario)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}
