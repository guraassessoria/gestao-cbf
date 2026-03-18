from datetime import datetime
from pydantic import BaseModel

from src.models.enums import StatusCompetencia
from src.schemas.common import ORMModel


class CompetenciaCreate(BaseModel):
    referencia: str


class CompetenciaOut(ORMModel):
    id: int
    referencia: str
    status: StatusCompetencia
    criada_em: datetime
