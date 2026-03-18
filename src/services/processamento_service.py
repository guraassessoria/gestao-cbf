from collections import defaultdict
from decimal import Decimal

from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session

from src.models.entities import (
    BalanceteItem,
    CustosFutebolItem,
    EstruturaBalancoItem,
    EstruturaDreItem,
    PlanoContasItem,
    Processamento,
    ResultadoBalanco,
    ResultadoBalanceteClassificado,
    ResultadoDre,
    ValidacaoLog,
)
from src.models.enums import Severidade, StatusProcessamento


def _compute_hierarquia(itens, get_chave_fn, result_by_chave: dict) -> tuple[dict, dict]:
    """Retorna (cod_to_valor, is_sintetica).

    - Folhas: valor vem de result_by_chave via chave do item.
    - Sintéticas: valor = soma recursiva dos filhos (independe do campo `nivel`).
    """
    children: dict[str, list[str]] = defaultdict(list)
    for item in itens:
        if item.cod_pai:
            children[item.cod_pai].append(item.cod)

    is_sintetica = {item.cod: bool(children[item.cod]) for item in itens}

    cod_to_valor: dict[str, Decimal] = {
        item.cod: result_by_chave.get(get_chave_fn(item), Decimal("0"))
        for item in itens
    }

    # Propagação bottom-up via recursão com memoização —
    # garante ordem correta independente dos valores de `nivel`.
    computed: set[str] = set()

    def _resolve(cod: str) -> Decimal:
        if cod in computed:
            return cod_to_valor[cod]
        if is_sintetica[cod]:
            cod_to_valor[cod] = sum(
                (_resolve(c) for c in children[cod]),
                Decimal("0"),
            )
        computed.add(cod)
        return cod_to_valor[cod]

    for item in itens:
        _resolve(item.cod)

    return cod_to_valor, is_sintetica


def _resolve_lado(item, cod_to_item: dict, cache: dict) -> str:
    """Determina ATIVO ou PASSIVO_PL para um item do balanço.

    Prioridade:
    1. Campo `lado` explícito no item.
    2. Para nós raiz (sem cod_pai): infere pelo conteúdo de chave_balanco/descricao.
    3. Herda do ancestral raiz.
    """
    if item.cod in cache:
        return cache[item.cod]

    if item.lado:  # definido no CSV
        result = item.lado.upper()
    elif not item.cod_pai:  # raiz
        texto = ((item.chave_balanco or "") + " " + (item.descricao or "")).upper()
        result = "ATIVO" if "ATIVO" in texto else "PASSIVO_PL"
    else:  # herda do pai
        pai = cod_to_item.get(item.cod_pai)
        result = _resolve_lado(pai, cod_to_item, cache) if pai else "PASSIVO_PL"

    cache[item.cod] = result
    return result


def resultado_dre_hierarquico(db: Session, processamento: Processamento) -> list[dict]:
    itens = db.scalars(
        select(EstruturaDreItem)
        .where(EstruturaDreItem.estrutura_versao_id == processamento.versao_dre_id)
        .order_by(EstruturaDreItem.id)
    ).all()

    result_by_chave = {
        r.chave_dre: r.valor
        for r in db.scalars(
            select(ResultadoDre).where(ResultadoDre.processamento_id == processamento.id)
        ).all()
    }

    cod_to_valor, is_sintetica = _compute_hierarquia(
        itens, lambda i: i.chave_dre, result_by_chave
    )

    return [
        {
            "cod": item.cod,
            "descricao": item.descricao_dre,
            "nivel": item.nivel,
            "cod_pai": item.cod_pai,
            "chave_dre": item.chave_dre,
            "valor": cod_to_valor[item.cod],
            "is_sintetica": is_sintetica[item.cod],
        }
        for item in itens
    ]


def resultado_balanco_hierarquico(db: Session, processamento: Processamento) -> dict:
    itens = db.scalars(
        select(EstruturaBalancoItem)
        .where(EstruturaBalancoItem.estrutura_versao_id == processamento.versao_balanco_id)
        .order_by(EstruturaBalancoItem.id)
    ).all()

    result_by_chave = {
        r.chave_balanco: r.valor
        for r in db.scalars(
            select(ResultadoBalanco).where(ResultadoBalanco.processamento_id == processamento.id)
        ).all()
    }

    cod_to_valor, is_sintetica = _compute_hierarquia(
        itens, lambda i: i.chave_balanco, result_by_chave
    )

    cod_to_item = {item.cod: item for item in itens}
    lado_cache: dict[str, str] = {}

    linhas = [
        {
            "cod": item.cod,
            "descricao": item.descricao,
            "nivel": item.nivel,
            "cod_pai": item.cod_pai,
            "chave_balanco": item.chave_balanco,
            "valor": cod_to_valor[item.cod],
            "is_sintetica": is_sintetica[item.cod],
            "lado": _resolve_lado(item, cod_to_item, lado_cache),
        }
        for item in itens
    ]

    return {
        "ativo": [l for l in linhas if l["lado"] == "ATIVO"],
        "passivo_pl": [l for l in linhas if l["lado"] == "PASSIVO_PL"],
    }


def processar(db: Session, processamento: Processamento) -> dict:
    erros = db.scalar(
        select(func.count(ValidacaoLog.id)).where(
            ValidacaoLog.processamento_id == processamento.id,
            ValidacaoLog.severidade == Severidade.ERRO,
        )
    )
    if erros and erros > 0:
        raise ValueError("Existem erros de validação. Corrija antes de processar.")

    db.execute(delete(ResultadoBalanco).where(ResultadoBalanco.processamento_id == processamento.id))
    db.execute(delete(ResultadoDre).where(ResultadoDre.processamento_id == processamento.id))
    db.execute(delete(ResultadoBalanceteClassificado).where(ResultadoBalanceteClassificado.processamento_id == processamento.id))
    db.flush()

    plano_map = {
        item.conta_contabil: item
        for item in db.scalars(
            select(PlanoContasItem).where(PlanoContasItem.estrutura_versao_id == processamento.versao_plano_contas_id)
        ).all()
    }
    dre_map = {
        item.chave_dre: item.descricao_dre
        for item in db.scalars(
            select(EstruturaDreItem).where(EstruturaDreItem.estrutura_versao_id == processamento.versao_dre_id)
        ).all()
    }
    balanco_map = {
        item.chave_balanco: item.descricao
        for item in db.scalars(
            select(EstruturaBalancoItem).where(EstruturaBalancoItem.estrutura_versao_id == processamento.versao_balanco_id)
        ).all()
    }

    total_balanco = defaultdict(lambda: Decimal("0"))
    total_dre = defaultdict(lambda: Decimal("0"))

    balancete_rows = db.scalars(select(BalanceteItem).where(BalanceteItem.processamento_id == processamento.id)).all()
    for row in balancete_rows:
        plano_item = plano_map.get(row.conta_contabil)
        if not plano_item:
            continue
        if plano_item.chave_balanco:
            total_balanco[plano_item.chave_balanco] += row.saldo_final
        if plano_item.chave_dre:
            total_dre[plano_item.chave_dre] += row.saldo_final

        db.add(
            ResultadoBalanceteClassificado(
                processamento_id=processamento.id,
                conta_contabil=row.conta_contabil,
                descricao_conta=row.descricao_conta,
                natureza=plano_item.natureza,
                chave_balanco=plano_item.chave_balanco,
                chave_dre=plano_item.chave_dre,
                saldo_final=row.saldo_final,
            )
        )

    custos_rows = db.scalars(select(CustosFutebolItem).where(CustosFutebolItem.processamento_id == processamento.id)).all()
    for row in custos_rows:
        total_dre[row.chave_dre] += row.valor

    for chave_balanco, valor in total_balanco.items():
        db.add(
            ResultadoBalanco(
                processamento_id=processamento.id,
                chave_balanco=chave_balanco,
                descricao=balanco_map.get(chave_balanco, chave_balanco),
                valor=valor,
            )
        )

    for chave_dre, valor in total_dre.items():
        db.add(
            ResultadoDre(
                processamento_id=processamento.id,
                chave_dre=chave_dre,
                descricao=dre_map.get(chave_dre, chave_dre),
                valor=valor,
            )
        )

    processamento.status = StatusProcessamento.PROCESSADO
    db.commit()
    return {
        "status": processamento.status,
        "total_linhas_balanco": len(total_balanco),
        "total_linhas_dre": len(total_dre),
        "total_linhas_balancete_classificado": len(balancete_rows),
    }
