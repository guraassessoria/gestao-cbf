from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EstruturaTipo(Base):
    __tablename__ = "estrutura_tipo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)


class EstruturaVersao(Base):
    __tablename__ = "estrutura_versao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estrutura_tipo_id: Mapped[int] = mapped_column(ForeignKey("estrutura_tipo.id"), nullable=False, index=True)
    versao: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    publicada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    criada_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    observacao: Mapped[str | None] = mapped_column(Text)

    tipo = relationship("EstruturaTipo")
    criada_por = relationship("Usuario")

    __table_args__ = (
        UniqueConstraint("estrutura_tipo_id", "versao", name="uq_estrutura_versao"),
    )


class PlanoContasItem(Base):
    __tablename__ = "plano_contas_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estrutura_versao_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False, index=True)
    conta_contabil: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    descricao_conta: Mapped[str] = mapped_column(String(255), nullable=False)
    classe_conta: Mapped[str | None] = mapped_column(String(80))
    natureza: Mapped[str] = mapped_column(String(20), nullable=False)
    chave_balanco: Mapped[str | None] = mapped_column(String(80))
    chave_dre: Mapped[str | None] = mapped_column(String(80))
    aceita_movimento: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    conta_pai: Mapped[str | None] = mapped_column(String(60))

    __table_args__ = (
        UniqueConstraint("estrutura_versao_id", "conta_contabil", name="uq_plano_conta"),
    )


class EstruturaDreItem(Base):
    __tablename__ = "estrutura_dre_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estrutura_versao_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False, index=True)
    cod: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao_dre: Mapped[str] = mapped_column(String(255), nullable=False)
    classe_dre: Mapped[str | None] = mapped_column(String(120))
    cod_pai: Mapped[str | None] = mapped_column(String(60))
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    chave_dre: Mapped[str] = mapped_column(String(80), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("estrutura_versao_id", "cod", name="uq_dre_cod"),
    )


class EstruturaBalancoItem(Base):
    __tablename__ = "estrutura_balanco_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estrutura_versao_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False, index=True)
    cod: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    cod_pai: Mapped[str | None] = mapped_column(String(60))
    chave_balanco: Mapped[str] = mapped_column(String(80), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("estrutura_versao_id", "cod", name="uq_balanco_cod"),
    )


class Competencia(Base):
    __tablename__ = "competencia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referencia: Mapped[str] = mapped_column(String(7), unique=True, nullable=False, index=True)  # YYYY-MM
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ABERTA")
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    criada_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))

    criada_por = relationship("Usuario")


class Processamento(Base):
    __tablename__ = "processamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencia.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="CRIADO")
    motivo_reprocessamento: Mapped[str | None] = mapped_column(Text)
    versao_plano_contas_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False)
    versao_dre_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False)
    versao_balanco_id: Mapped[int] = mapped_column(ForeignKey("estrutura_versao.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    criado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))

    competencia = relationship("Competencia")
    criado_por = relationship("Usuario")


class ArquivoCarga(Base):
    __tablename__ = "arquivo_carga"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    tipo_arquivo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    conteudo_texto: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="RECEBIDO")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BalanceteItem(Base):
    __tablename__ = "balancete_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    conta_contabil: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    descricao_conta: Mapped[str] = mapped_column(String(255), nullable=False)
    saldo_anterior: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    debito: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    credito: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    movimentacao: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    saldo_final: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)


class CustosFutebolItem(Base):
    __tablename__ = "custos_futebol_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    sub_descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    chave_dre: Mapped[str] = mapped_column(String(80), nullable=False)


class ValidacaoLog(Base):
    __tablename__ = "validacao_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    arquivo_tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    severidade: Mapped[str] = mapped_column(String(10), nullable=False)  # ERRO | ALERTA
    linha: Mapped[int | None] = mapped_column(Integer)
    campo: Mapped[str | None] = mapped_column(String(80))
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ResultadoBalanco(Base):
    __tablename__ = "resultado_balanco"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    chave_balanco: Mapped[str] = mapped_column(String(80), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)


class ResultadoDre(Base):
    __tablename__ = "resultado_dre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    chave_dre: Mapped[str] = mapped_column(String(80), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)


class ResultadoBalanceteClassificado(Base):
    __tablename__ = "resultado_balancete_classificado"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processamento_id: Mapped[int] = mapped_column(ForeignKey("processamento.id"), nullable=False, index=True)
    conta_contabil: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao_conta: Mapped[str] = mapped_column(String(255), nullable=False)
    natureza: Mapped[str] = mapped_column(String(20), nullable=False)
    chave_balanco: Mapped[str | None] = mapped_column(String(80))
    chave_dre: Mapped[str | None] = mapped_column(String(80))
    saldo_final: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
