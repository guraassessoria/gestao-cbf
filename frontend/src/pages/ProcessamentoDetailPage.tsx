import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../lib/api'
import type {
  Processamento,
  ValidacaoLog,
  LinhaHierarquicaBalanco,
  LinhaHierarquicaDre,
  ResultadoBalancoHierarquico,
  ResultadoBalanceteClassificado,
  ArquivoCarga,
  ValidacaoResult,
  ProcessamentoResult,
} from '../lib/types'
import {
  ArrowLeft,
  Upload,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  FileCheck2,
  Loader2,
  RefreshCw,
} from 'lucide-react'

type Tab = 'resumo' | 'validacoes' | 'balanco' | 'dre' | 'classificado'

export default function ProcessamentoDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [proc, setProc] = useState<Processamento | null>(null)
  const [arquivos, setArquivos] = useState<ArquivoCarga[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<Tab>('resumo')
  const [actionLoading, setActionLoading] = useState(false)
  const [actionMsg, setActionMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Tab data
  const [validacoes, setValidacoes] = useState<ValidacaoLog[]>([])
  const [balanco, setBalanco] = useState<ResultadoBalancoHierarquico | null>(null)
  const [dre, setDre] = useState<LinhaHierarquicaDre[]>([])
  const [classificado, setClassificado] = useState<ResultadoBalanceteClassificado[]>([])

  const loadProc = async () => {
    try {
      const [p, a] = await Promise.all([
        api.get<Processamento>(`/processamentos/${id}`),
        api.get<ArquivoCarga[]>(`/processamentos/${id}/arquivos`),
      ])
      setProc(p.data)
      setArquivos(a.data)
    } catch {
      setError('Processamento não encontrado')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProc()
  }, [id])

  useEffect(() => {
    if (!proc) return
    if (tab === 'validacoes') {
      api.get<ValidacaoLog[]>(`/processamentos/${id}/validacoes`).then((r) => setValidacoes(r.data))
    } else if (tab === 'balanco') {
      api
        .get<ResultadoBalancoHierarquico>(`/processamentos/${id}/resultado/balanco/hierarquico`)
        .then((r) => setBalanco(r.data))
        .catch(() => setBalanco({ ativo: [], passivo_pl: [] }))
    } else if (tab === 'dre') {
      api
        .get<LinhaHierarquicaDre[]>(`/processamentos/${id}/resultado/dre/hierarquico`)
        .then((r) => setDre(r.data))
        .catch(() => setDre([]))
    } else if (tab === 'classificado') {
      api
        .get<ResultadoBalanceteClassificado[]>(`/processamentos/${id}/resultado/balancete-classificado`)
        .then((r) => setClassificado(r.data))
    }
  }, [tab, proc])

  const uploadFile = async (tipo: 'balancete' | 'custos-futebol', file: File) => {
    setActionLoading(true)
    setActionMsg(null)
    const formData = new FormData()
    formData.append('arquivo', file)
    try {
      await api.post(`/processamentos/${id}/upload-${tipo}`, formData)
      setActionMsg({ type: 'success', text: `Arquivo ${tipo} enviado com sucesso!` })
      loadProc()
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Erro ao enviar arquivo' })
    } finally {
      setActionLoading(false)
    }
  }

  const validar = async () => {
    setActionLoading(true)
    setActionMsg(null)
    try {
      const res = await api.post<ValidacaoResult>(`/processamentos/${id}/validar`)
      setActionMsg({
        type: res.data.errors > 0 ? 'error' : 'success',
        text: `Validação concluída: ${res.data.errors} erros, ${res.data.alerts} alertas. Status: ${res.data.status}`,
      })
      loadProc()
      setTab('validacoes')
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Erro na validação' })
    } finally {
      setActionLoading(false)
    }
  }

  const processar = async () => {
    setActionLoading(true)
    setActionMsg(null)
    try {
      const res = await api.post<ProcessamentoResult>(`/processamentos/${id}/processar`)
      setActionMsg({
        type: 'success',
        text: `Processado! Balanço: ${res.data.total_linhas_balanco}, DRE: ${res.data.total_linhas_dre}, Classificado: ${res.data.total_linhas_balancete_classificado}`,
      })
      loadProc()
      setTab('balanco')
    } catch (err: any) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Erro no processamento' })
    } finally {
      setActionLoading(false)
    }
  }

  const statusConfig = (s: string) => {
    switch (s) {
      case 'CRIADO': return { color: 'bg-gray-100 text-gray-700', icon: null }
      case 'ARQUIVOS_RECEBIDOS': return { color: 'bg-yellow-100 text-yellow-700', icon: Upload }
      case 'VALIDADO': return { color: 'bg-blue-100 text-blue-700', icon: CheckCircle2 }
      case 'VALIDADO_COM_ERROS': return { color: 'bg-red-100 text-red-700', icon: XCircle }
      case 'PROCESSADO': return { color: 'bg-green-100 text-green-700', icon: CheckCircle2 }
      default: return { color: 'bg-gray-100 text-gray-700', icon: null }
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    )
  }

  if (error || !proc) {
    return (
      <div className="text-center py-20">
        <XCircle className="mx-auto h-12 w-12 text-red-400" />
        <p className="mt-4 text-lg font-medium text-gray-700">{error || 'Processamento não encontrado'}</p>
        <button
          onClick={() => navigate('/processamentos')}
          className="mt-4 text-sm text-brand-600 hover:underline"
        >
          Voltar
        </button>
      </div>
    )
  }

  const cfg = statusConfig(proc.status)

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center gap-4">
        <button
          onClick={() => navigate('/processamentos')}
          className="rounded-lg border p-2 hover:bg-gray-50"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Processamento #{proc.id}</h1>
          <p className="text-sm text-gray-500">
            Competência ID {proc.competencia_id} · Criado em{' '}
            {new Date(proc.criado_em).toLocaleDateString('pt-BR')}
          </p>
        </div>
        <span className={`ml-auto rounded-full px-3 py-1 text-sm font-medium ${cfg.color}`}>
          {proc.status}
        </span>
      </div>

      {/* Action messages */}
      {actionMsg && (
        <div
          className={`mb-4 flex items-center gap-2 rounded-lg border px-4 py-3 text-sm ${
            actionMsg.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-700'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}
        >
          {actionMsg.type === 'success' ? (
            <CheckCircle2 className="h-4 w-4 shrink-0" />
          ) : (
            <AlertTriangle className="h-4 w-4 shrink-0" />
          )}
          {actionMsg.text}
        </div>
      )}

      {/* Workflow Actions */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Upload Balancete */}
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-gray-700">1. Upload Balancete</p>
          <input
            type="file"
            accept=".csv,.xlsx"
            disabled={actionLoading}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) uploadFile('balancete', f)
            }}
            className="w-full text-xs file:mr-2 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-brand-700"
          />
          {arquivos.find((a) => a.tipo_arquivo === 'BALANCETE') && (
            <p className="mt-1 text-xs text-green-600">
              ✓ {arquivos.find((a) => a.tipo_arquivo === 'BALANCETE')!.nome_arquivo}
            </p>
          )}
        </div>

        {/* Upload Custos */}
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-gray-700">2. Upload Custos Futebol</p>
          <input
            type="file"
            accept=".csv,.xlsx"
            disabled={actionLoading}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) uploadFile('custos-futebol', f)
            }}
            className="w-full text-xs file:mr-2 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-brand-700"
          />
          {arquivos.find((a) => a.tipo_arquivo === 'CUSTOS_FUTEBOL') && (
            <p className="mt-1 text-xs text-green-600">
              ✓ {arquivos.find((a) => a.tipo_arquivo === 'CUSTOS_FUTEBOL')!.nome_arquivo}
            </p>
          )}
        </div>

        {/* Validar */}
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-gray-700">3. Validar</p>
          <button
            onClick={validar}
            disabled={actionLoading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600 disabled:opacity-50"
          >
            {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileCheck2 className="h-4 w-4" />}
            Validar Dados
          </button>
        </div>

        {/* Processar */}
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-gray-700">4. Processar</p>
          <button
            onClick={processar}
            disabled={actionLoading || proc.status === 'VALIDADO_COM_ERROS'}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            Processar
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-4 flex gap-1 rounded-lg border bg-white p-1">
        {(
          [
            ['resumo', 'Resumo'],
            ['validacoes', 'Validações'],
            ['balanco', 'Balanço'],
            ['dre', 'DRE'],
            ['classificado', 'Classificado'],
          ] as [Tab, string][]
        ).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === key ? 'bg-brand-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="rounded-xl border bg-white shadow-sm">
        {tab === 'resumo' && (
          <div className="p-6">
            <h3 className="mb-4 text-lg font-semibold">Informações do Processamento</h3>
            <dl className="grid gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-gray-500">ID</dt>
                <dd className="font-medium">{proc.id}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Status</dt>
                <dd><span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{proc.status}</span></dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Competência ID</dt>
                <dd className="font-medium">{proc.competencia_id}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Criado em</dt>
                <dd className="font-medium">{new Date(proc.criado_em).toLocaleString('pt-BR')}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Versão Plano Contas</dt>
                <dd className="font-medium">{proc.versao_plano_contas_id}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Versão DRE</dt>
                <dd className="font-medium">{proc.versao_dre_id}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Versão Balanço</dt>
                <dd className="font-medium">{proc.versao_balanco_id}</dd>
              </div>
              {proc.motivo_reprocessamento && (
                <div className="sm:col-span-2">
                  <dt className="text-sm text-gray-500">Motivo Reprocessamento</dt>
                  <dd className="font-medium">{proc.motivo_reprocessamento}</dd>
                </div>
              )}
            </dl>

            {arquivos.length > 0 && (
              <>
                <h3 className="mb-3 mt-6 text-lg font-semibold">Arquivos</h3>
                <div className="space-y-2">
                  {arquivos.map((a) => (
                    <div key={a.id} className="flex items-center gap-3 rounded-lg border px-4 py-3">
                      <Upload className="h-4 w-4 text-gray-400" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{a.nome_arquivo}</p>
                        <p className="text-xs text-gray-400">{a.tipo_arquivo}</p>
                      </div>
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          a.status === 'VÁLIDO'
                            ? 'bg-green-100 text-green-700'
                            : a.status === 'INVÁLIDO'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {a.status}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {tab === 'validacoes' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">Severidade</th>
                  <th className="px-6 py-3">Arquivo</th>
                  <th className="px-6 py-3">Linha</th>
                  <th className="px-6 py-3">Campo</th>
                  <th className="px-6 py-3">Mensagem</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {validacoes.map((v) => (
                  <tr key={v.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3">
                      {v.severidade === 'ERRO' ? (
                        <span className="flex items-center gap-1 text-red-600">
                          <XCircle className="h-4 w-4" /> ERRO
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-amber-600">
                          <AlertTriangle className="h-4 w-4" /> ALERTA
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3 font-medium">{v.arquivo_tipo}</td>
                    <td className="px-6 py-3 text-gray-500">{v.linha ?? '—'}</td>
                    <td className="px-6 py-3 text-gray-500">{v.campo ?? '—'}</td>
                    <td className="px-6 py-3">{v.mensagem}</td>
                  </tr>
                ))}
                {validacoes.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                      Nenhuma validação registrada. Execute a validação primeiro.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'balanco' && (() => {
          const fmt = (v: number) =>
            Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2 })

          const renderLado = (itens: LinhaHierarquicaBalanco[]) =>
            itens.length === 0 ? (
              <p className="py-6 text-center text-sm text-gray-400">Sem dados.</p>
            ) : (
              <div className="divide-y">
                {itens.map((item) => (
                  <div
                    key={item.cod}
                    style={{ paddingLeft: `${(item.nivel - 1) * 20}px` }}
                    className={`flex items-baseline justify-between gap-4 px-4 py-2 text-sm ${
                      item.is_sintetica
                        ? 'bg-gray-50 font-semibold text-gray-900'
                        : 'text-gray-700'
                    }`}
                  >
                    <span className="min-w-0 truncate">{item.descricao}</span>
                    <span className="shrink-0 font-mono tabular-nums">{fmt(item.valor)}</span>
                  </div>
                ))}
              </div>
            )

          const isEmpty = !balanco || (balanco.ativo.length === 0 && balanco.passivo_pl.length === 0)

          if (isEmpty) {
            return (
              <div className="px-6 py-8 text-center text-gray-400">
                Nenhum resultado de balanço. Processe os dados primeiro.
              </div>
            )
          }

          return (
            <div className="grid grid-cols-1 divide-y lg:grid-cols-2 lg:divide-x lg:divide-y-0">
              <div>
                <div className="border-b bg-gray-100 px-4 py-2 text-xs font-bold uppercase tracking-wider text-gray-600">
                  Ativo
                </div>
                {renderLado(balanco!.ativo)}
              </div>
              <div>
                <div className="border-b bg-gray-100 px-4 py-2 text-xs font-bold uppercase tracking-wider text-gray-600">
                  Passivo e Patrimônio Líquido
                </div>
                {renderLado(balanco!.passivo_pl)}
              </div>
            </div>
          )
        })()}

        {tab === 'dre' && (() => {
          // Post-order: filhos aparecem antes do pai (totalizador ao final do grupo)
          function drePostOrder(itens: LinhaHierarquicaDre[]): LinhaHierarquicaDre[] {
            const byPai = new Map<string | null, LinhaHierarquicaDre[]>()
            for (const item of itens) {
              const key = item.cod_pai ?? null
              if (!byPai.has(key)) byPai.set(key, [])
              byPai.get(key)!.push(item)
            }
            const result: LinhaHierarquicaDre[] = []
            function visit(pai: string | null) {
              for (const child of byPai.get(pai) ?? []) {
                visit(child.cod)
                result.push(child)
              }
            }
            visit(null)
            return result
          }

          const ordenados = drePostOrder(dre)

          return (
            <div>
              {ordenados.length === 0 ? (
                <div className="px-6 py-8 text-center text-gray-400">
                  Nenhum resultado de DRE. Processe os dados primeiro.
                </div>
              ) : (
                <div className="divide-y">
                  {ordenados.map((item) => (
                    <div
                      key={item.cod}
                      style={{ paddingLeft: `${(item.nivel - 1) * 20}px` }}
                      className={`flex items-baseline justify-between gap-4 px-4 py-2 text-sm ${
                        item.is_sintetica
                          ? 'bg-gray-50 font-semibold text-gray-900'
                          : 'text-gray-700'
                      }`}
                    >
                      <span className="min-w-0 truncate">
                        {item.is_sintetica ? `(=) ${item.descricao}` : item.descricao}
                      </span>
                      <span className="shrink-0 font-mono tabular-nums">
                        {Number(item.valor).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })()}

        {tab === 'classificado' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">Conta</th>
                  <th className="px-6 py-3">Descrição</th>
                  <th className="px-6 py-3">Natureza</th>
                  <th className="px-6 py-3">Chave Balanço</th>
                  <th className="px-6 py-3">Chave DRE</th>
                  <th className="px-6 py-3 text-right">Saldo Final</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {classificado.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 font-mono text-xs font-medium">{c.conta_contabil}</td>
                    <td className="px-6 py-3">{c.descricao_conta}</td>
                    <td className="px-6 py-3">{c.natureza}</td>
                    <td className="px-6 py-3 text-gray-500">{c.chave_balanco ?? '—'}</td>
                    <td className="px-6 py-3 text-gray-500">{c.chave_dre ?? '—'}</td>
                    <td className="px-6 py-3 text-right font-mono">
                      {Number(c.saldo_final).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
                {classificado.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-400">
                      Nenhum resultado classificado. Processe os dados primeiro.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
