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


def processar(db: Session, processamento: Processamento) -> dict:
    erros = db.scalar(
        select(func.count(ValidacaoLog.id)).where(
            ValidacaoLog.processamento_id == processamento.id,
            ValidacaoLog.severidade == "ERRO",
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

    processamento.status = "PROCESSADO"
    db.commit()
    return {
        "status": processamento.status,
        "total_linhas_balanco": len(total_balanco),
        "total_linhas_dre": len(total_dre),
        "total_linhas_balancete_classificado": len(balancete_rows),
    }
