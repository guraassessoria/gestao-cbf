from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

from src.models.enums import Severidade, StatusProcessamento, TipoArquivo
from src.schemas.common import ORMModel


class ProcessamentoCreate(BaseModel):
    competencia_id: int


class ReprocessamentoCreate(BaseModel):
    motivo: str


class ProcessamentoOut(ORMModel):
    id: int
    competencia_id: int
    status: StatusProcessamento
    motivo_reprocessamento: str | None
    versao_plano_contas_id: int
    versao_dre_id: int
    versao_balanco_id: int
    criado_em: datetime


class ValidacaoLogOut(ORMModel):
    id: int
    arquivo_tipo: TipoArquivo
    severidade: Severidade
    linha: int | None
    campo: str | None
    mensagem: str


class ResultadoBalancoOut(ORMModel):
    id: int
    chave_balanco: str
    descricao: str
    valor: Decimal


class ResultadoDreOut(ORMModel):
    id: int
    chave_dre: str
    descricao: str
    valor: Decimal


class ResultadoBalanceteClassificadoOut(ORMModel):
    id: int
    conta_contabil: str
    descricao_conta: str
    natureza: str
    chave_balanco: str | None
    chave_dre: str | None
    saldo_final: Decimal
