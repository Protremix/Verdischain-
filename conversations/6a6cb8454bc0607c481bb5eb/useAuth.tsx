import { useState, useEffect, useCallback, createContext, useContext, type ReactNode } from 'react'
import { auth, setToken, clearToken, type User } from '@/lib/api'

interface AuthState {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('evolvixos_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const me = await auth.me()
      setUser(me)
    } catch {
      clearToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string) => {
    const tokens = await auth.login(email, password)
    setToken(tokens.access_token)
    const me = await auth.me()
    setUser(me)
  }

  const logout = () => {
    clearToken()
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated: !!user, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
