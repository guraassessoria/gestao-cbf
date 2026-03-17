import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { EstruturaVersao, EstruturasEmProducao } from '../lib/types'
import { useAuth } from '../contexts/AuthContext'
import { Upload, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

const TIPOS = [
  { codigo: 'plano-contas', label: 'Plano de Contas', endpoint: '/estruturas/plano-contas/upload' },
  { codigo: 'dre', label: 'Estrutura DRE', endpoint: '/estruturas/dre/upload' },
  { codigo: 'balanco', label: 'Estrutura Balanço', endpoint: '/estruturas/balanco/upload' },
] as const

export default function EstruturasPage() {
  const { isAdmin } = useAuth()
  const [versoes, setVersoes] = useState<EstruturaVersao[]>([])
  const [producao, setProducao] = useState<EstruturasEmProducao | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploadTipo, setUploadTipo] = useState<typeof TIPOS[number] | null>(null)
  const [versaoName, setVersaoName] = useState('')
  const [observacao, setObservacao] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const load = async () => {
    const [v, p] = await Promise.all([
      api.get<EstruturaVersao[]>('/estruturas/versoes'),
      api.get<EstruturasEmProducao>('/estruturas/em-producao'),
    ])
    setVersoes(v.data)
    setProducao(p.data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadTipo || !file) return
    setUploading(true)
    setMsg(null)
    const formData = new FormData()
    formData.append('versao', versaoName)
    formData.append('observacao', observacao)
    formData.append('arquivo', file)
    try {
      await api.post(uploadTipo.endpoint, formData)
      setMsg({ type: 'success', text: `${uploadTipo.label} publicado com sucesso!` })
      setUploadTipo(null)
      setVersaoName('')
      setObservacao('')
      setFile(null)
      load()
    } catch (err: any) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Erro ao enviar arquivo' })
    } finally {
      setUploading(false)
    }
  }

  const statusBadge = (status: string) => {
    if (status === 'EM_PRODUCAO')
      return <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">Em Produção</span>
    return <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">Substituída</span>
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Estruturas</h1>
      </div>

      {msg && (
        <div
          className={`mb-4 flex items-center gap-2 rounded-lg border px-4 py-3 text-sm ${
            msg.type === 'success'
              ? 'border-green-200 bg-green-50 text-green-700'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}
        >
          {msg.type === 'success' ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          {msg.text}
        </div>
      )}

      {/* Produção Summary */}
      {producao && (
        <div className="mb-8 grid gap-4 sm:grid-cols-3">
          {[
            { label: 'Plano de Contas', v: producao.plano_contas },
            { label: 'DRE', v: producao.dre },
            { label: 'Balanço', v: producao.balanco },
          ].map((item) => (
            <div key={item.label} className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm font-medium text-gray-500">{item.label}</p>
              {item.v ? (
                <>
                  <p className="mt-1 text-lg font-bold text-gray-900">v{item.v.versao}</p>
                  <p className="text-xs text-gray-400">
                    {item.v.publicada_em
                      ? new Date(item.v.publicada_em).toLocaleDateString('pt-BR')
                      : ''}
                  </p>
                </>
              ) : (
                <p className="mt-1 text-sm text-amber-600">Não configurado</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Cards */}
      {isAdmin && (
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Upload de Estruturas</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {TIPOS.map((tipo) => (
              <button
                key={tipo.codigo}
                onClick={() => {
                  setUploadTipo(tipo)
                  setMsg(null)
                }}
                className="flex items-center gap-3 rounded-xl border bg-white p-5 text-left shadow-sm transition-colors hover:border-brand-300 hover:bg-brand-50"
              >
                <Upload className="h-5 w-5 text-brand-600" />
                <div>
                  <p className="font-medium text-gray-900">Upload {tipo.label}</p>
                  <p className="text-xs text-gray-500">Enviar novo CSV</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {uploadTipo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
            <h2 className="mb-4 text-lg font-bold">Upload {uploadTipo.label}</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Versão</label>
                <input
                  required
                  value={versaoName}
                  onChange={(e) => setVersaoName(e.target.value)}
                  placeholder="Ex: 2026-03"
                  className="w-full rounded-lg border px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Observação</label>
                <input
                  value={observacao}
                  onChange={(e) => setObservacao(e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Arquivo CSV</label>
                <input
                  type="file"
                  required
                  accept=".csv"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="w-full rounded-lg border px-3 py-2 text-sm file:mr-4 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1 file:text-sm file:font-medium file:text-brand-700"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setUploadTipo(null)}
                  className="rounded-lg border px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                >
                  {uploading ? 'Enviando...' : 'Publicar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Versões Table */}
      <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
        <div className="border-b px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">Histórico de Versões</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-6 py-3">ID</th>
              <th className="px-6 py-3">Versão</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Publicada em</th>
              <th className="px-6 py-3">Observação</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {versoes.map((v) => (
              <tr key={v.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 text-gray-500">{v.id}</td>
                <td className="px-6 py-3 font-medium">{v.versao}</td>
                <td className="px-6 py-3">{statusBadge(v.status)}</td>
                <td className="px-6 py-3 text-gray-500">
                  {v.publicada_em ? new Date(v.publicada_em).toLocaleDateString('pt-BR') : '—'}
                </td>
                <td className="px-6 py-3 text-gray-500">{v.observacao || '—'}</td>
              </tr>
            ))}
            {versoes.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                  Nenhuma versão cadastrada. Faça upload das estruturas para começar.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
