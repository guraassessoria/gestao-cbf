from datetime import datetime
from pydantic import BaseModel

from src.schemas.common import ORMModel


class EstruturaVersaoOut(ORMModel):
    id: int
    estrutura_tipo_id: int
    versao: str
    status: str
    publicada_em: datetime | None
    observacao: str | None


class EstruturasEmProducaoResponse(BaseModel):
    plano_contas: EstruturaVersaoOut | None
    dre: EstruturaVersaoOut | None
    balanco: EstruturaVersaoOut | None
