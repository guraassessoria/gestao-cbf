from decimal import Decimal

from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session

from src.models.entities import (
    ArquivoCarga,
    BalanceteItem,
    CustosFutebolItem,
    EstruturaDreItem,
    PlanoContasItem,
    Processamento,
    ValidacaoLog,
)
from src.models.enums import Severidade, StatusArquivo, StatusProcessamento, TipoArquivo
from src.services.csv_tools import parse_date_br, parse_decimal, parse_semicolon_csv


BALANCETE_HEADERS = {
    "data", "conta_contabil", "descricao_conta", "saldo_anterior", "debito", "credito", "movimentacao", "saldo_final"
}
CUSTOS_HEADERS = {"data", "descricao", "sub_descricao", "valor", "chave_dre"}


def _add_log(db: Session, processamento_id: int, arquivo_tipo: TipoArquivo, severidade: Severidade, mensagem: str, linha: int | None = None, campo: str | None = None):
    db.add(
        ValidacaoLog(
            processamento_id=processamento_id,
            arquivo_tipo=arquivo_tipo,
            severidade=severidade,
            linha=linha,
            campo=campo,
            mensagem=mensagem,
        )
    )


def validar_processamento(db: Session, processamento: Processamento) -> dict:
    db.execute(delete(ValidacaoLog).where(ValidacaoLog.processamento_id == processamento.id))
    db.execute(delete(BalanceteItem).where(BalanceteItem.processamento_id == processamento.id))
    db.execute(delete(CustosFutebolItem).where(CustosFutebolItem.processamento_id == processamento.id))
    db.flush()

    arquivos = db.scalars(select(ArquivoCarga).where(ArquivoCarga.processamento_id == processamento.id)).all()
    por_tipo = {a.tipo_arquivo: a for a in arquivos}

    has_error = False

    if TipoArquivo.BALANCETE not in por_tipo:
        _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, "Arquivo de balancete não enviado")
        has_error = True
    if TipoArquivo.CUSTOS_FUTEBOL not in por_tipo:
        _add_log(db, processamento.id, TipoArquivo.CUSTOS_FUTEBOL, Severidade.ERRO, "Arquivo de custos com futebol não enviado")
        has_error = True

    plano_contas = {
        item.conta_contabil: item
        for item in db.scalars(
            select(PlanoContasItem).where(PlanoContasItem.estrutura_versao_id == processamento.versao_plano_contas_id)
        ).all()
    }
    chaves_dre = {
        item.chave_dre
        for item in db.scalars(
            select(EstruturaDreItem).where(EstruturaDreItem.estrutura_versao_id == processamento.versao_dre_id)
        ).all()
    }

    if TipoArquivo.BALANCETE in por_tipo:
        arquivo = por_tipo[TipoArquivo.BALANCETE]
        rows = parse_semicolon_csv(arquivo.conteudo_texto)
        if not rows:
            _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, "Arquivo de balancete sem dados")
            has_error = True
        if rows and not BALANCETE_HEADERS.issubset(rows[0].keys()):
            _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, "Cabeçalhos obrigatórios ausentes")
            has_error = True

        for idx, row in enumerate(rows, start=2):
            try:
                data = parse_date_br(row["data"])
                saldo_anterior = parse_decimal(row["saldo_anterior"])
                debito = parse_decimal(row["debito"])
                credito = parse_decimal(row["credito"])
                movimentacao = parse_decimal(row["movimentacao"])
                saldo_final = parse_decimal(row["saldo_final"])
                conta = row["conta_contabil"]
                descricao = row["descricao_conta"]

                if conta not in plano_contas:
                    # Conta sintética não cadastrada no plano (ex: totalizadoras exportadas
                    # pelo sistema contábil): ignorada silenciosamente
                    continue

                plano_item = plano_contas[conta]
                if not plano_item.aceita_movimento:
                    # Conta sintética marcada no plano: ignorada silenciosamente
                    continue

                if movimentacao != (debito - credito):
                    has_error = True
                    _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, "Movimentação divergente de débito-crédito", idx, "movimentacao")
                    continue

                if saldo_final != (saldo_anterior + movimentacao):
                    has_error = True
                    _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, "Saldo final divergente", idx, "saldo_final")
                    continue

                if plano_item.natureza == "1" and saldo_final < Decimal("0"):
                    _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ALERTA, "Saldo final negativo em conta de ativo", idx, "saldo_final")

                db.add(
                    BalanceteItem(
                        processamento_id=processamento.id,
                        data=data,
                        conta_contabil=conta,
                        descricao_conta=descricao,
                        saldo_anterior=saldo_anterior,
                        debito=debito,
                        credito=credito,
                        movimentacao=movimentacao,
                        saldo_final=saldo_final,
                    )
                )
            except Exception as exc:
                has_error = True
                _add_log(db, processamento.id, TipoArquivo.BALANCETE, Severidade.ERRO, str(exc), idx)

    if TipoArquivo.CUSTOS_FUTEBOL in por_tipo:
        arquivo = por_tipo[TipoArquivo.CUSTOS_FUTEBOL]
        rows = parse_semicolon_csv(arquivo.conteudo_texto)
        if not rows:
            _add_log(db, processamento.id, TipoArquivo.CUSTOS_FUTEBOL, Severidade.ERRO, "Arquivo de custos sem dados")
            has_error = True
        if rows and not CUSTOS_HEADERS.issubset(rows[0].keys()):
            _add_log(db, processamento.id, TipoArquivo.CUSTOS_FUTEBOL, Severidade.ERRO, "Cabeçalhos obrigatórios ausentes")
            has_error = True

        for idx, row in enumerate(rows, start=2):
            try:
                data = parse_date_br(row["data"])
                valor = parse_decimal(row["valor"])
                descricao = row["descricao"]
                sub_descricao = row["sub_descricao"]
                chave_dre = row["chave_dre"]

                if not chave_dre:
                    # Linha sintética/totalizadora sem chave_dre: ignorada silenciosamente
                    continue
                if not descricao or not sub_descricao:
                    raise ValueError("Descrição e sub_descricao são obrigatórias")
                if chave_dre not in chaves_dre:
                    raise ValueError("chave_dre não existe na estrutura DRE congelada")

                db.add(
                    CustosFutebolItem(
                        processamento_id=processamento.id,
                        data=data,
                        descricao=descricao,
                        sub_descricao=sub_descricao,
                        valor=valor,
                        chave_dre=chave_dre,
                    )
                )
            except Exception as exc:
                has_error = True
                _add_log(db, processamento.id, TipoArquivo.CUSTOS_FUTEBOL, Severidade.ERRO, str(exc), idx)

    processamento.status = StatusProcessamento.VALIDADO_COM_ERROS if has_error else StatusProcessamento.VALIDADO
    for arquivo in arquivos:
        arquivo.status = StatusArquivo.INVALIDO if has_error else StatusArquivo.VALIDO

    db.commit()

    errors = db.scalar(
        select(func.count(ValidacaoLog.id)).where(
            ValidacaoLog.processamento_id == processamento.id,
            ValidacaoLog.severidade == Severidade.ERRO,
        )
    )
    alerts = db.scalar(
        select(func.count(ValidacaoLog.id)).where(
            ValidacaoLog.processamento_id == processamento.id,
            ValidacaoLog.severidade == Severidade.ALERTA,
        )
    )
    return {"status": processamento.status, "errors": errors or 0, "alerts": alerts or 0}
