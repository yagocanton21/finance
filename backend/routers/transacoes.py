import calendar
import uuid
from datetime import date
from decimal import Decimal, ROUND_DOWN

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.transacoes import Transacao
from backend.models.usuarios import Usuario
from backend.schemas.transacoes import (
    TransacaoCreate,
    TransacaoResponse,
    TransacaoUpdate,
)
from backend.security import obter_usuario_atual

router = APIRouter(prefix="/transacoes", tags=["Transações"])


def somar_meses(data_base: date, meses: int) -> date:
    """Calcula a data somando meses, respeitando o último dia do mês (ex: 31 de janeiro -> 28/29 de fevereiro)."""
    mes = (data_base.month - 1 + meses) % 12 + 1
    ano = data_base.year + (data_base.month - 1 + meses) // 12
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, min(data_base.day, ultimo_dia))


# Rota para listar transações do usuário logado (com filtros opcionais)
@router.get("/", response_model=list[TransacaoResponse])
def listar_transacoes(
    tipo: str | None = None,
    categoria_id: int | None = None,
    pago: bool | None = None,
    usuario: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    # Busca apenas as transações do usuário autenticado.
    query = db.query(Transacao).filter(Transacao.usuario_id == usuario.id)

    # Aplica os filtros informados na requisição.
    if tipo:
        query = query.filter(Transacao.tipo == tipo.upper())
    if categoria_id:
        query = query.filter(Transacao.categoria_id == categoria_id)
    if pago is not None:
        query = query.filter(Transacao.pago == pago)

    return query.order_by(Transacao.data_vencimento.asc()).all()


def buscar_transacao_do_usuario(
    transacao_id: int,
    usuario_id: int,
    db: Session,
) -> Transacao:
    """Busca uma transação garantindo que ela pertença ao usuário atual."""
    # A consulta pelo usuário impede o acesso a transações de outras contas.
    transacao = (
        db.query(Transacao)
        .filter(
            Transacao.id == transacao_id,
            Transacao.usuario_id == usuario_id,
        )
        .first()
    )
    if not transacao:
        # Não informa se o ID existe para outro usuário.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )
    return transacao


# Rota para buscar uma transação pelo ID.
@router.get("/{transacao_id}", response_model=TransacaoResponse)
def buscar_transacao(
    transacao_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db),
):
    return buscar_transacao_do_usuario(transacao_id, usuario.id, db)


# Rota para criar transação (simples ou parcelada)
@router.post("/", response_model=TransacaoResponse | list[TransacaoResponse], status_code=status.HTTP_201_CREATED)
def criar_transacao(
    transacao: TransacaoCreate,
    usuario: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    data_base = transacao.data_vencimento or date.today()

    # Dados iguais para uma transação simples e para todas as parcelas.
    dados_comuns = {
        "usuario_id": usuario.id,
        "categoria_id": transacao.categoria_id,
        "tipo": transacao.tipo.upper(),
    }

    # Transação simples (compra única ou receita).
    if transacao.total_parcelas == 1:
        nova_transacao = Transacao(
            **dados_comuns,
            descricao=transacao.descricao,
            valor=transacao.valor,
            data_vencimento=data_base,
            pago=transacao.pago,
            parcela_atual=1,
            total_parcelas=1,
            grupo_id=None,
        )
        # Salva e atualiza o objeto com o ID gerado pelo banco.
        db.add(nova_transacao)
        db.commit()
        db.refresh(nova_transacao)
        return nova_transacao

    # Transação parcelada: todas as parcelas compartilham um grupo.
    grupo_id = str(uuid.uuid4())
    total_parcelas = transacao.total_parcelas
    valor_parcela = (transacao.valor / total_parcelas).quantize(
        Decimal("0.01"),
        rounding=ROUND_DOWN,
    )

    # A última parcela recebe os centavos restantes, preservando o valor total.
    valores_parcelas = [valor_parcela] * (total_parcelas - 1)
    valores_parcelas.append(transacao.valor - sum(valores_parcelas, Decimal("0.00")))

    transacoes_criadas = [
        Transacao(
            **dados_comuns,
            descricao=f"{transacao.descricao} ({numero}/{total_parcelas})",
            valor=valor,
            data_vencimento=somar_meses(data_base, numero - 1),
            pago=transacao.pago if numero == 1 else False,
            parcela_atual=numero,
            total_parcelas=total_parcelas,
            grupo_id=grupo_id,
        )
        for numero, valor in enumerate(valores_parcelas, start=1)
    ]

    # Salva todas as parcelas em uma única operação.
    db.add_all(transacoes_criadas)
    db.commit()
    for parcela in transacoes_criadas:
        db.refresh(parcela)

    return transacoes_criadas


# Rota para atualizar uma transação. Aceita PUT e PATCH.
@router.put("/{transacao_id}", response_model=TransacaoResponse)
@router.patch("/{transacao_id}", response_model=TransacaoResponse)
def atualizar_transacao(
    transacao_id: int,
    dados: TransacaoUpdate,
    usuario: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db),
):
    # Busca a transação e garante que ela é do usuário logado.
    transacao = buscar_transacao_do_usuario(transacao_id, usuario.id, db)

    # Atualiza somente os campos enviados no corpo da requisição.
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if campo == "tipo" and valor is not None:
            valor = valor.upper()
        setattr(transacao, campo, valor)

    db.commit()
    db.refresh(transacao)
    return transacao


# Rota para excluir uma transação pelo ID.
@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_transacao(
    transacao_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(get_db),
):
    transacao = buscar_transacao_do_usuario(transacao_id, usuario.id, db)

    # Remove a transação encontrada e confirma a alteração no banco.
    db.delete(transacao)
    db.commit()
