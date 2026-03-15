import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user, require_roles
from src.models.entities import Competencia, Usuario
from src.schemas.competencia import CompetenciaCreate, CompetenciaOut

router = APIRouter(prefix="/competencias", tags=["competencias"])


@router.get("", response_model=list[CompetenciaOut], dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def listar_competencias(db: Session = Depends(get_db)):
    return db.scalars(select(Competencia).order_by(Competencia.referencia.desc())).all()


@router.post("", response_model=CompetenciaOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def criar_competencia(
    payload: CompetenciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not re.fullmatch(r"\d{4}-\d{2}", payload.referencia):
        raise HTTPException(status_code=400, detail="Formato de competência deve ser YYYY-MM")
    existing = db.scalar(select(Competencia).where(Competencia.referencia == payload.referencia))
    if existing:
        raise HTTPException(status_code=400, detail="Competência já existe")
    comp = Competencia(referencia=payload.referencia, status="ABERTA", criada_por_id=current_user.id)
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp


@router.get("/{competencia_id}", response_model=CompetenciaOut, dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL"))])
def obter_competencia(competencia_id: int, db: Session = Depends(get_db)):
    comp = db.get(Competencia, competencia_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competência não encontrada")
    return comp
