from enum import Enum


class Perfil(str, Enum):
    ADMIN = "ADMIN"
    OPERACIONAL = "OPERACIONAL"
    CONSULTA = "CONSULTA"


class StatusCompetencia(str, Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"


class StatusProcessamento(str, Enum):
    CRIADO = "CRIADO"
    ARQUIVOS_RECEBIDOS = "ARQUIVOS_RECEBIDOS"
    VALIDADO = "VALIDADO"
    VALIDADO_COM_ERROS = "VALIDADO_COM_ERROS"
    PROCESSADO = "PROCESSADO"


class StatusEstruturaVersao(str, Enum):
    EM_PRODUCAO = "EM_PRODUCAO"
    SUBSTITUIDA = "SUBSTITUIDA"


class TipoEstrutura(str, Enum):
    PLANO_CONTAS = "PLANO_CONTAS"
    DRE = "DRE"
    BALANCO = "BALANCO"


class TipoArquivo(str, Enum):
    BALANCETE = "BALANCETE"
    CUSTOS_FUTEBOL = "CUSTOS_FUTEBOL"


class Severidade(str, Enum):
    ERRO = "ERRO"
    ALERTA = "ALERTA"


class StatusArquivo(str, Enum):
    RECEBIDO = "RECEBIDO"
    VALIDO = "VÁLIDO"
    INVALIDO = "INVÁLIDO"
