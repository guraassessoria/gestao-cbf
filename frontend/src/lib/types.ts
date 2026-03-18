// ───── Auth ─────
export interface LoginRequest {
  email: string
  senha: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  nome: string
  email: string
  perfil: 'ADMIN' | 'OPERACIONAL' | 'CONSULTA'
  ativo: boolean
}

// ───── Usuarios ─────
export interface UsuarioCreate {
  nome: string
  email: string
  senha: string
  perfil: string
}

export interface UsuarioUpdate {
  nome?: string
  senha?: string
  perfil?: string
  ativo?: boolean
}

// ───── Competencias ─────
export interface CompetenciaCreate {
  referencia: string
}

export interface Competencia {
  id: number
  referencia: string
  status: string
  criada_em: string
}

// ───── Estruturas ─────
export interface EstruturaVersao {
  id: number
  estrutura_tipo_id: number
  versao: string
  status: string
  publicada_em: string | null
  observacao: string | null
}

export interface EstruturasEmProducao {
  plano_contas: EstruturaVersao | null
  dre: EstruturaVersao | null
  balanco: EstruturaVersao | null
}

// ───── Processamentos ─────
export interface Processamento {
  id: number
  competencia_id: number
  status: string
  motivo_reprocessamento: string | null
  versao_plano_contas_id: number
  versao_dre_id: number
  versao_balanco_id: number
  criado_em: string
}

export interface ProcessamentoCreate {
  competencia_id: number
}

export interface ValidacaoLog {
  id: number
  arquivo_tipo: string
  severidade: 'ERRO' | 'ALERTA'
  linha: number | null
  campo: string | null
  mensagem: string
}

export interface ResultadoBalanco {
  id: number
  chave_balanco: string
  descricao: string
  valor: number
}

export interface ResultadoDre {
  id: number
  chave_dre: string
  descricao: string
  valor: number
}

export interface LinhaHierarquicaBalanco {
  cod: string
  descricao: string
  nivel: number
  cod_pai: string | null
  chave_balanco: string
  valor: number
  is_sintetica: boolean
  lado: string | null
}

export interface LinhaHierarquicaDre {
  cod: string
  descricao: string
  nivel: number
  cod_pai: string | null
  chave_dre: string
  valor: number
  is_sintetica: boolean
}

export interface ResultadoBalancoHierarquico {
  ativo: LinhaHierarquicaBalanco[]
  passivo_pl: LinhaHierarquicaBalanco[]
}

export interface ResultadoBalanceteClassificado {
  id: number
  conta_contabil: string
  descricao_conta: string
  natureza: string
  chave_balanco: string | null
  chave_dre: string | null
  saldo_final: number
}

export interface ArquivoCarga {
  id: number
  tipo_arquivo: string
  nome_arquivo: string
  status: string
  criado_em: string
}

// ───── Dashboard ─────
export interface DashboardData {
  estruturas_em_producao: Array<{
    tipo: string
    versao: string
    publicada_em: string
  }>
  ultima_competencia: {
    id: number
    referencia: string
    status: string
  } | null
  total_processamentos: number
}

export interface ValidacaoResult {
  status: string
  errors: number
  alerts: number
}

export interface ProcessamentoResult {
  status: string
  total_linhas_balanco: number
  total_linhas_dre: number
  total_linhas_balancete_classificado: number
}
