import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import api from '../lib/api'
import type { UserInfo, LoginRequest, TokenResponse } from '../lib/types'

interface AuthContextType {
  user: UserInfo | null
  token: string | null
  loading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  isAdmin: boolean
  isOperacional: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api
        .get<UserInfo>('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('token')
          setToken(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (credentials: LoginRequest) => {
    const res = await api.post<TokenResponse>('/auth/login', credentials)
    const newToken = res.data.access_token
    localStorage.setItem('token', newToken)
    setToken(newToken)
    const me = await api.get<UserInfo>('/auth/me', {
      headers: { Authorization: `Bearer ${newToken}` },
    })
    setUser(me.data)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        isAdmin: user?.perfil === 'ADMIN',
        isOperacional: user?.perfil === 'OPERACIONAL',
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
