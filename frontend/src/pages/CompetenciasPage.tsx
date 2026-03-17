import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { Competencia, CompetenciaCreate } from '../lib/types'
import { Plus, Loader2, AlertCircle } from 'lucide-react'

export default function CompetenciasPage() {
  const [competencias, setCompetencias] = useState<Competencia[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [referencia, setReferencia] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    api.get<Competencia[]>('/competencias').then((res) => {
      setCompetencias(res.data)
      setLoading(false)
    })
  }

  useEffect(load, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await api.post('/competencias', { referencia } as CompetenciaCreate)
      setShowModal(false)
      setReferencia('')
      load()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar competência')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Competências</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Nova Competência
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
                <th className="px-6 py-3">Referência</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Criada em</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {competencias.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 text-gray-500">{c.id}</td>
                  <td className="px-6 py-3 font-medium">{c.referencia}</td>
                  <td className="px-6 py-3">
                    <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                      {c.status}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-gray-500">
                    {new Date(c.criada_em).toLocaleDateString('pt-BR')}
                  </td>
                </tr>
              ))}
              {competencias.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-400">
                    Nenhuma competência cadastrada.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
            <h2 className="mb-4 text-lg font-bold">Nova Competência</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Referência (AAAA-MM)
                </label>
                <input
                  required
                  value={referencia}
                  onChange={(e) => setReferencia(e.target.value)}
                  placeholder="2026-03"
                  pattern="\d{4}-\d{2}"
                  className="w-full rounded-lg border px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
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
