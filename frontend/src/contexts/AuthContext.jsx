/**
 * AuthContext
 *
 * Provides authentication state (user, token) throughout the app.
 * Token is stored in localStorage for development simplicity.
 *
 * ⚠️  Security note: localStorage is accessible to any JS on the page.
 *     For production, prefer httpOnly cookies managed server-side.
 */

import { createContext, useState, useCallback, useMemo } from 'react'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,  setUser]  = useState(() => {
    try { return JSON.parse(localStorage.getItem('aquapura_user')) } catch { return null }
  })
  const [token, setToken] = useState(() => localStorage.getItem('aquapura_token') ?? null)

  const login = useCallback((userData, accessToken) => {
    setUser(userData)
    setToken(accessToken)
    localStorage.setItem('aquapura_user',  JSON.stringify(userData))
    localStorage.setItem('aquapura_token', accessToken)
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('aquapura_user')
    localStorage.removeItem('aquapura_token')
  }, [])

  const value = useMemo(() => ({ user, token, login, logout }), [user, token, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
