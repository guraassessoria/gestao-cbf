from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.models.entities import (
    EstruturaBalancoItem,
    EstruturaDreItem,
    EstruturaTipo,
    EstruturaVersao,
    PlanoContasItem,
)
from src.services.csv_tools import parse_semicolon_csv


NATUREZAS_ACEITAS = {"1", "2", "3.1", "3.2.1", "3.2.2", "3.2.3", "3.2.4", "3.4"}


def _get_tipo(db: Session, codigo: str) -> EstruturaTipo:
    tipo = db.scalar(select(EstruturaTipo).where(EstruturaTipo.codigo == codigo))
    if not tipo:
        raise ValueError(f"Tipo estrutural não encontrado: {codigo}")
    return tipo


def publicar_nova_versao(db: Session, tipo_codigo: str, versao: str, observacao: str | None, user_id: int, content: str):
    tipo = _get_tipo(db, tipo_codigo)
    rows = parse_semicolon_csv(content)
    if not rows:
        raise ValueError("Arquivo estrutural sem linhas de dados")

    existing = db.scalar(
        select(EstruturaVersao).where(
            EstruturaVersao.estrutura_tipo_id == tipo.id,
            EstruturaVersao.versao == versao,
        )
    )
    if existing:
        raise ValueError("Já existe uma versão com esse identificador")

    nova_versao = EstruturaVersao(
        estrutura_tipo_id=tipo.id,
        versao=versao,
        status="EM_PRODUCAO",
        publicada_em=datetime.now(timezone.utc),
        criada_por_id=user_id,
        observacao=observacao,
    )
    db.add(nova_versao)
    db.flush()

    db.execute(
        update(EstruturaVersao)
        .where(EstruturaVersao.estrutura_tipo_id == tipo.id, EstruturaVersao.id != nova_versao.id)
        .values(status="SUBSTITUIDA")
    )

    if tipo_codigo == "PLANO_CONTAS":
        contas = set()
        for idx, row in enumerate(rows, start=2):
            conta = row.get("conta_contabil", "")
            natureza = row.get("natureza", "")
            if not conta:
                raise ValueError(f"Linha {idx}: conta_contabil obrigatória")
            if conta in contas:
                raise ValueError(f"Linha {idx}: conta_contabil duplicada")
            contas.add(conta)
            if natureza not in NATUREZAS_ACEITAS:
                raise ValueError(f"Linha {idx}: natureza inválida")
            db.add(
                PlanoContasItem(
                    estrutura_versao_id=nova_versao.id,
                    conta_contabil=conta,
                    descricao_conta=row.get("descricao_conta", ""),
                    classe_conta=row.get("classe conta", ""),
                    natureza=natureza,
                    chave_balanco=row.get("chave_balanco") or None,
                    chave_dre=row.get("chave_dre") or None,
                    aceita_movimento=(row.get("aceita_movimento", "").lower() in {"1", "true", "sim", "s", "x", "yes"}),
                    nivel=int(row.get("nivel", "1")),
                    conta_pai=row.get("conta_pai") or None,
                )
            )

    elif tipo_codigo == "DRE":
        codes = set()
        for idx, row in enumerate(rows, start=2):
            cod = row.get("cod", "")
            if not cod:
                raise ValueError(f"Linha {idx}: cod obrigatório")
            if cod in codes:
                raise ValueError(f"Linha {idx}: cod duplicado")
            codes.add(cod)
            db.add(
                EstruturaDreItem(
                    estrutura_versao_id=nova_versao.id,
                    cod=cod,
                    descricao_dre=row.get("descricao_dre", ""),
                    classe_dre=row.get("classe_dre") or None,
                    cod_pai=row.get("cod_pai") or None,
                    nivel=int(row.get("nivel", "1")),
                    chave_dre=row.get("chave_dre", ""),
                )
            )
    elif tipo_codigo == "BALANCO":
        codes = set()
        for idx, row in enumerate(rows, start=2):
            cod = row.get("cod", "")
            if not cod:
                raise ValueError(f"Linha {idx}: cod obrigatório")
            if cod in codes:
                raise ValueError(f"Linha {idx}: cod duplicado")
            codes.add(cod)
            db.add(
                EstruturaBalancoItem(
                    estrutura_versao_id=nova_versao.id,
                    cod=cod,
                    descricao=row.get("descricao", ""),
                    nivel=int(row.get("nivel", "1")),
                    cod_pai=row.get("cod_pai") or None,
                    chave_balanco=row.get("chave_balanco", ""),
                )
            )
    else:
        raise ValueError("Tipo estrutural inválido")

    db.commit()
    db.refresh(nova_versao)
    return nova_versao
