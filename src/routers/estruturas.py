from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.models.entities import EstruturaTipo, EstruturaVersao, Usuario
from src.models.enums import StatusEstruturaVersao, TipoEstrutura
from src.schemas.estrutura import EstruturaVersaoOut, EstruturasEmProducaoResponse
from src.services.estrutura_service import publicar_nova_versao

router = APIRouter(prefix="/estruturas", tags=["estruturas"])


def _decode_upload(file: UploadFile) -> str:
    raw = file.file.read()
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail="Não foi possível decodificar o arquivo")


@router.get("/versoes", response_model=list[EstruturaVersaoOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def listar_versoes(db: Session = Depends(get_db)):
    return db.scalars(select(EstruturaVersao).order_by(EstruturaVersao.criada_em.desc())).all()


@router.get("/em-producao", response_model=EstruturasEmProducaoResponse, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def estruturas_em_producao(db: Session = Depends(get_db)):
    tipos = {t.codigo: t.id for t in db.scalars(select(EstruturaTipo)).all()}

    def get_version(codigo: str):
        tipo_id = tipos.get(codigo)
        if not tipo_id:
            return None
        return db.scalar(
            select(EstruturaVersao)
            .where(EstruturaVersao.estrutura_tipo_id == tipo_id, EstruturaVersao.status == StatusEstruturaVersao.EM_PRODUCAO)
            .order_by(EstruturaVersao.publicada_em.desc())
        )

    return EstruturasEmProducaoResponse(
        plano_contas=get_version("PLANO_CONTAS"),
        dre=get_version("DRE"),
        balanco=get_version("BALANCO"),
    )


@router.post("/plano-contas/upload", response_model=EstruturaVersaoOut, dependencies=[Depends(require_roles("ADMIN"))])
def upload_plano_contas(
    versao: str = Form(...),
    observacao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        created = publicar_nova_versao(db, "PLANO_CONTAS", versao, observacao, current_user.id, _decode_upload(arquivo))
        return created
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/dre/upload", response_model=EstruturaVersaoOut, dependencies=[Depends(require_roles("ADMIN"))])
def upload_dre(
    versao: str = Form(...),
    observacao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        created = publicar_nova_versao(db, "DRE", versao, observacao, current_user.id, _decode_upload(arquivo))
        return created
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/balanco/upload", response_model=EstruturaVersaoOut, dependencies=[Depends(require_roles("ADMIN"))])
def upload_balanco(
    versao: str = Form(...),
    observacao: str | None = Form(None),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        created = publicar_nova_versao(db, "BALANCO", versao, observacao, current_user.id, _decode_upload(arquivo))
        return created
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
