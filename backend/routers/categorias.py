from backend.database import get_db
from backend.models.categorias import Categoria
from backend.schemas.categorias import CategoriaCreate, CategoriaResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


# router para categorias
router = APIRouter(prefix="/categorias", tags=["categorias"])

# rota para criar uma categoria
@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    
    # 1. Verificar se a categoria já existe no banco
    verifica_categoria = db.query(Categoria).filter(Categoria.nome == categoria.nome).first()
    if verifica_categoria:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Categoria já existente"
        )

    # 2. Criar a nova categoria
    nova_categoria = Categoria(
        nome=categoria.nome
    )

    # 3. Salvar no banco de dados
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria

# rota para listar categorias
@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):

    # busca todas as categorias no banco de dados
    categorias = db.query(Categoria).all()
    return categorias

# rota para listar uma categoria por id
@router.get("/{id}", response_model=CategoriaResponse)
def listar_categoria_por_id(id: int, db: Session = Depends(get_db)):
    
    # busca a categoria pelo id
    categoria = db.query(Categoria).filter(Categoria.id == id).first()

    # se nao houver categoria, retorna um erro 404
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return categoria

# rota para atualizar uma categoria
@router.put("/{id}", response_model=CategoriaResponse, status_code=status.HTTP_200_OK)
def atualizar_categoria(id: int, dados_categoria: CategoriaCreate, db: Session = Depends(get_db)):
    
    # 1. Busca a categoria que será alterada
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")

    # 2. Verifica se o novo nome de categoria já está sendo usado por outra categoria
    categoria_existente = db.query(Categoria).filter(Categoria.nome == dados_categoria.nome, Categoria.id != id).first()
    if categoria_existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existente")

    # 3. Atualiza os dados
    categoria.nome = dados_categoria.nome

    # 4. Salva no banco de dados
    db.commit()
    db.refresh(categoria)
    return categoria

# rota para deletar uma categoria
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def deletar_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")

    db.delete(categoria)
    db.commit()
    return {"message": "Categoria deletada com sucesso"}