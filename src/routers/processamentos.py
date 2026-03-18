from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.models.enums import StatusCompetencia, StatusEstruturaVersao, StatusProcessamento, TipoArquivo
from src.services.csv_tools import parse_xlsx_to_csv_text
from src.models.entities import (
    ArquivoCarga,
    BalanceteItem,
    Competencia,
    EstruturaTipo,
    EstruturaVersao,
    EstruturaBalancoItem,
    EstruturaDreItem,
    Processamento,
    ResultadoBalanco,
    ResultadoBalanceteClassificado,
    ResultadoDre,
    Usuario,
    ValidacaoLog,
)
from src.schemas.processamento import (
    ProcessamentoCreate,
    ProcessamentoOut,
    ReprocessamentoCreate,
    ResultadoBalanceteClassificadoOut,
    ResultadoBalancoOut,
    ResultadoDreOut,
    ResultadoBalancoHierarquicoOut,
    LinhaHierarquicaDreOut,
    ValidacaoLogOut,
)
from src.services.processamento_service import processar, resultado_balanco_hierarquico, resultado_dre_hierarquico
from src.services.validacao_service import validar_processamento

router = APIRouter(prefix="/processamentos", tags=["processamentos"])


def _decode_upload(file: UploadFile) -> str:
    raw = file.file.read()
    fname = (file.filename or "").lower()
    if fname.endswith(".xlsx") or raw[:4] == b"PK\x03\x04":
        try:
            return parse_xlsx_to_csv_text(raw)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo xlsx: {exc}")
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail="Não foi possível decodificar o arquivo")


def _estrutura_em_producao(db: Session, codigo: str):
    tipo = db.scalar(select(EstruturaTipo).where(EstruturaTipo.codigo == codigo))
    if not tipo:
        raise HTTPException(status_code=400, detail=f"Tipo estrutural ausente: {codigo}")
    versao = db.scalar(
        select(EstruturaVersao)
        .where(EstruturaVersao.estrutura_tipo_id == tipo.id, EstruturaVersao.status == StatusEstruturaVersao.EM_PRODUCAO)
        .order_by(EstruturaVersao.publicada_em.desc())
    )
    if not versao:
        raise HTTPException(status_code=400, detail=f"Não existe versão em produção para {codigo}")
    return versao


def _get_processamento(db: Session, processamento_id: int) -> Processamento:
    processamento = db.get(Processamento, processamento_id)
    if not processamento:
        raise HTTPException(status_code=404, detail="Processamento não encontrado")
    return processamento


@router.get("", response_model=list[ProcessamentoOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def listar_processamentos(db: Session = Depends(get_db)):
    return db.scalars(select(Processamento).order_by(Processamento.criado_em.desc())).all()


@router.post("", response_model=ProcessamentoOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def criar_processamento(
    payload: ProcessamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    competencia = db.get(Competencia, payload.competencia_id)
    if not competencia:
        raise HTTPException(status_code=404, detail="Competência não encontrada")
    if competencia.status == StatusCompetencia.FECHADA:
        raise HTTPException(status_code=400, detail="Não é possível criar processamento para uma competência fechada")

    proc = Processamento(
        competencia_id=payload.competencia_id,
        status=StatusProcessamento.CRIADO,
        versao_plano_contas_id=_estrutura_em_producao(db, "PLANO_CONTAS").id,
        versao_dre_id=_estrutura_em_producao(db, "DRE").id,
        versao_balanco_id=_estrutura_em_producao(db, "BALANCO").id,
        criado_por_id=current_user.id,
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc


@router.post("/{processamento_id}/reprocessar", response_model=ProcessamentoOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def reprocessar(
    processamento_id: int,
    payload: ReprocessamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    original = _get_processamento(db, processamento_id)
    if not payload.motivo.strip():
        raise HTTPException(status_code=400, detail="Motivo obrigatório")

    proc = Processamento(
        competencia_id=original.competencia_id,
        status=StatusProcessamento.CRIADO,
        motivo_reprocessamento=payload.motivo,
        versao_plano_contas_id=original.versao_plano_contas_id,
        versao_dre_id=original.versao_dre_id,
        versao_balanco_id=original.versao_balanco_id,
        criado_por_id=current_user.id,
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return proc


@router.get("/{processamento_id}", response_model=ProcessamentoOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def obter_processamento(processamento_id: int, db: Session = Depends(get_db)):
    return _get_processamento(db, processamento_id)


@router.post("/{processamento_id}/upload-balancete", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def upload_balancete(
    processamento_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    processamento = _get_processamento(db, processamento_id)
    arquivo_obj = ArquivoCarga(
        processamento_id=processamento.id,
        tipo_arquivo=TipoArquivo.BALANCETE,
        nome_arquivo=arquivo.filename or "balancete.csv",
        conteudo_texto=_decode_upload(arquivo),
        status="RECEBIDO",
    )
    db.add(arquivo_obj)
    processamento.status = StatusProcessamento.ARQUIVOS_RECEBIDOS
    db.commit()
    return {"message": "Balancete enviado com sucesso"}


@router.post("/{processamento_id}/upload-custos-futebol", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def upload_custos(
    processamento_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    processamento = _get_processamento(db, processamento_id)
    arquivo_obj = ArquivoCarga(
        processamento_id=processamento.id,
        tipo_arquivo=TipoArquivo.CUSTOS_FUTEBOL,
        nome_arquivo=arquivo.filename or "custos_futebol.csv",
        conteudo_texto=_decode_upload(arquivo),
        status="RECEBIDO",
    )
    db.add(arquivo_obj)
    processamento.status = StatusProcessamento.ARQUIVOS_RECEBIDOS
    db.commit()
    return {"message": "Custos com futebol enviados com sucesso"}


@router.post("/{processamento_id}/validar", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def validar(processamento_id: int, db: Session = Depends(get_db)):
    processamento = _get_processamento(db, processamento_id)
    try:
        return validar_processamento(db, processamento)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{processamento_id}/processar", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def processar_execucao(processamento_id: int, db: Session = Depends(get_db)):
    processamento = _get_processamento(db, processamento_id)
    try:
        return processar(db, processamento)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{processamento_id}/validacoes", response_model=list[ValidacaoLogOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def listar_validacoes(processamento_id: int, db: Session = Depends(get_db)):
    _get_processamento(db, processamento_id)
    return db.scalars(select(ValidacaoLog).where(ValidacaoLog.processamento_id == processamento_id).order_by(ValidacaoLog.id)).all()


@router.get("/{processamento_id}/resultado/resumo", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_resumo(processamento_id: int, db: Session = Depends(get_db)):
    """Diagnóstico: mostra contadores das tabelas para verificar se dados foram gerados."""
    processamento = _get_processamento(db, processamento_id)
    return {
        "processamento_id": processamento_id,
        "status": processamento.status,
        "versao_balanco_id": processamento.versao_balanco_id,
        "versao_dre_id": processamento.versao_dre_id,
        "total_estrutura_balanco_itens": db.scalar(
            select(func.count(EstruturaBalancoItem.id)).where(
                EstruturaBalancoItem.estrutura_versao_id == processamento.versao_balanco_id
            )
        ),
        "total_estrutura_dre_itens": db.scalar(
            select(func.count(EstruturaDreItem.id)).where(
                EstruturaDreItem.estrutura_versao_id == processamento.versao_dre_id
            )
        ),
        "total_resultado_balanco": db.scalar(
            select(func.count(ResultadoBalanco.id)).where(
                ResultadoBalanco.processamento_id == processamento_id
            )
        ),
        "total_resultado_dre": db.scalar(
            select(func.count(ResultadoDre.id)).where(
                ResultadoDre.processamento_id == processamento_id
            )
        ),
        "total_balancete_itens": db.scalar(
            select(func.count(BalanceteItem.id)).where(
                BalanceteItem.processamento_id == processamento_id
            )
        ),
    }


@router.get("/{processamento_id}/resultado/balanco", response_model=list[ResultadoBalancoOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_balanco(processamento_id: int, db: Session = Depends(get_db)):
    _get_processamento(db, processamento_id)
    return db.scalars(
        select(ResultadoBalanco)
        .where(ResultadoBalanco.processamento_id == processamento_id)
        .order_by(ResultadoBalanco.id)
    ).all()


@router.get("/{processamento_id}/resultado/dre", response_model=list[ResultadoDreOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_dre(processamento_id: int, db: Session = Depends(get_db)):
    _get_processamento(db, processamento_id)
    return db.scalars(
        select(ResultadoDre)
        .where(ResultadoDre.processamento_id == processamento_id)
        .order_by(ResultadoDre.id)
    ).all()


@router.get("/{processamento_id}/resultado/balanco/hierarquico", response_model=ResultadoBalancoHierarquicoOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_balanco_hierarquico_endpoint(processamento_id: int, db: Session = Depends(get_db)):
    processamento = _get_processamento(db, processamento_id)
    if processamento.status != StatusProcessamento.PROCESSADO:
        raise HTTPException(
            status_code=400,
            detail=f"Processamento ainda não foi concluído. Status atual: {processamento.status}",
        )
    return resultado_balanco_hierarquico(db, processamento)


@router.get("/{processamento_id}/resultado/dre/hierarquico", response_model=list[LinhaHierarquicaDreOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_dre_hierarquico_endpoint(processamento_id: int, db: Session = Depends(get_db)):
    processamento = _get_processamento(db, processamento_id)
    if processamento.status != StatusProcessamento.PROCESSADO:
        raise HTTPException(
            status_code=400,
            detail=f"Processamento ainda não foi concluído. Status atual: {processamento.status}",
        )
    return resultado_dre_hierarquico(db, processamento)


@router.get("/{processamento_id}/resultado/balancete-classificado", response_model=list[ResultadoBalanceteClassificadoOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def resultado_balancete(processamento_id: int, db: Session = Depends(get_db)):
    _get_processamento(db, processamento_id)
    return db.scalars(
        select(ResultadoBalanceteClassificado)
        .where(ResultadoBalanceteClassificado.processamento_id == processamento_id)
        .order_by(ResultadoBalanceteClassificado.id)
    ).all()


@router.get("/{processamento_id}/arquivos", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def listar_arquivos(processamento_id: int, db: Session = Depends(get_db)):
    _get_processamento(db, processamento_id)
    arquivos = db.scalars(select(ArquivoCarga).where(ArquivoCarga.processamento_id == processamento_id).order_by(ArquivoCarga.id)).all()
    return [
        {
            "id": arq.id,
            "tipo_arquivo": arq.tipo_arquivo,
            "nome_arquivo": arq.nome_arquivo,
            "status": arq.status,
            "criado_em": arq.criado_em,
        }
        for arq in arquivos
    ]
