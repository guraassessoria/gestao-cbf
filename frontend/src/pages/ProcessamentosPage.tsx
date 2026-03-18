import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import type { Competencia, Processamento } from '../lib/types'
import { Plus, Loader2, Eye, AlertCircle } from 'lucide-react'

export default function ProcessamentosPage() {
  const navigate = useNavigate()
  const [competencias, setCompetencias] = useState<Competencia[]>([])
  const [processamentos, setProcessamentos] = useState<Processamento[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedComp, setSelectedComp] = useState<number | ''>('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    Promise.all([
      api.get<Competencia[]>('/competencias'),
      api.get<Processamento[]>('/processamentos'),
    ]).then(([comps, procs]) => {
      setCompetencias(comps.data)
      setProcessamentos(procs.data)
      setLoading(false)
    })
  }

  useEffect(load, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedComp) return
    setError('')
    setSaving(true)
    try {
      const res = await api.post<Processamento>('/processamentos', {
        competencia_id: Number(selectedComp),
      })
      navigate(`/processamentos/${res.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar processamento')
    } finally {
      setSaving(false)
    }
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'CRIADO': return 'bg-gray-100 text-gray-700'
      case 'ARQUIVOS_RECEBIDOS': return 'bg-yellow-100 text-yellow-700'
      case 'VALIDADO': return 'bg-blue-100 text-blue-700'
      case 'VALIDADO_COM_ERROS': return 'bg-red-100 text-red-700'
      case 'PROCESSADO': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Processamentos</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Novo Processamento
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-6 py-3">ID</th>
                <th className="px-6 py-3">Competência</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Criado em</th>
                <th className="px-6 py-3">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {processamentos.map((p) => {
                const comp = competencias.find((c) => c.id === p.competencia_id)
                return (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 font-medium">{p.id}</td>
                    <td className="px-6 py-3">{comp?.referencia ?? p.competencia_id}</td>
                    <td className="px-6 py-3">
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(p.status)}`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-500">
                      {new Date(p.criado_em).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="px-6 py-3">
                      <button
                        onClick={() => navigate(`/processamentos/${p.id}`)}
                        className="flex items-center gap-1 text-sm text-brand-600 hover:underline"
                      >
                        <Eye className="h-4 w-4" /> Detalhes
                      </button>
                    </td>
                  </tr>
                )
              })}
              {processamentos.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                    Nenhum processamento criado. Clique em "Novo Processamento" para começar.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
            <h2 className="mb-4 text-lg font-bold">Novo Processamento</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Competência</label>
                <select
                  required
                  value={selectedComp}
                  onChange={(e) => setSelectedComp(Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                >
                  <option value="">Selecione...</option>
                  {competencias.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.referencia} ({c.status})
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-400">
                  As versões das estruturas em produção serão congeladas automaticamente.
                </p>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-lg border px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                >
                  {saving ? 'Criando...' : 'Criar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
