import { useEffect, useState } from 'react'
import api from '../lib/api'
import type { DashboardData } from '../lib/types'
import { BarChart3, Calendar, FolderTree, Loader2 } from 'lucide-react'

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<DashboardData>('/dashboard').then((res) => {
      setData(res.data)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
      </div>
    )
  }

  if (!data) return null

  const cards = [
    {
      title: 'Total Processamentos',
      value: data.total_processamentos,
      icon: BarChart3,
      color: 'bg-blue-50 text-blue-700',
      iconColor: 'text-blue-500',
    },
    {
      title: 'Última Competência',
      value: data.ultima_competencia?.referencia || '—',
      sub: data.ultima_competencia?.status,
      icon: Calendar,
      color: 'bg-green-50 text-green-700',
      iconColor: 'text-green-500',
    },
    {
      title: 'Estruturas em Produção',
      value: data.estruturas_em_producao.length,
      icon: FolderTree,
      color: 'bg-purple-50 text-purple-700',
      iconColor: 'text-purple-500',
    },
  ]

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.title} className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{card.title}</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{card.value}</p>
                {card.sub && (
                  <span className="mt-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                    {card.sub}
                  </span>
                )}
              </div>
              <div className={`rounded-xl p-3 ${card.color}`}>
                <card.icon className={`h-6 w-6 ${card.iconColor}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {data.estruturas_em_producao.length > 0 && (
        <div className="rounded-xl border bg-white shadow-sm">
          <div className="border-b px-6 py-4">
            <h2 className="text-lg font-semibold text-gray-900">Estruturas em Produção</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">Tipo</th>
                  <th className="px-6 py-3">Versão</th>
                  <th className="px-6 py-3">Publicada em</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.estruturas_em_producao.map((e, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-6 py-3 font-medium">{e.tipo}</td>
                    <td className="px-6 py-3">{e.versao}</td>
                    <td className="px-6 py-3 text-gray-500">
                      {e.publicada_em
                        ? new Date(e.publicada_em).toLocaleDateString('pt-BR')
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
