import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsuariosPage from './pages/UsuariosPage'
import EstruturasPage from './pages/EstruturasPage'
import CompetenciasPage from './pages/CompetenciasPage'
import ProcessamentosPage from './pages/ProcessamentosPage'
import ProcessamentoDetailPage from './pages/ProcessamentoDetailPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    )
  }
  return user ? <>{children}</> : <Navigate to="/login" />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="usuarios" element={<UsuariosPage />} />
        <Route path="estruturas" element={<EstruturasPage />} />
        <Route path="competencias" element={<CompetenciasPage />} />
        <Route path="processamentos" element={<ProcessamentosPage />} />
        <Route path="processamentos/:id" element={<ProcessamentoDetailPage />} />
      </Route>
    </Routes>
  )
}
