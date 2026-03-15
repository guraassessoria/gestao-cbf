from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from src.core.db import get_db
from src.core.deps import require_roles
from src.models.entities import Competencia, EstruturaTipo, EstruturaVersao, Processamento

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", dependencies=[Depends(require_roles("ADMIN", "OPERACIONAL", "CONSULTA"))])
def dashboard(db: Session = Depends(get_db)):
    estruturas = db.execute(
        select(EstruturaTipo.codigo, EstruturaVersao.versao, EstruturaVersao.publicada_em)
        .join(EstruturaVersao, EstruturaVersao.estrutura_tipo_id == EstruturaTipo.id)
        .where(EstruturaVersao.status == "EM_PRODUCAO")
    ).all()

    ultima_competencia = db.scalar(select(Competencia).order_by(Competencia.referencia.desc()))
    total_processamentos = db.scalar(select(func.count(Processamento.id))) or 0

    return {
        "estruturas_em_producao": [
            {"tipo": tipo, "versao": versao, "publicada_em": publicada_em}
            for tipo, versao, publicada_em in estruturas
        ],
        "ultima_competencia": (
            {
                "id": ultima_competencia.id,
                "referencia": ultima_competencia.referencia,
                "status": ultima_competencia.status,
            }
            if ultima_competencia
            else None
        ),
        "total_processamentos": total_processamentos,
    }
