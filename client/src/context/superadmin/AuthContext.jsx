import React, { createContext, useState, useContext, useEffect } from 'react'
import { authService } from '../../services/superadmin/auth.service'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('wilsy_token')
    if (token) {
      authService.getProfile()
        .then(setUser)
        .catch(() => localStorage.removeItem('wilsy_token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const response = await authService.login(email, password)
    localStorage.setItem('wilsy_token', response.token)
    setUser(response.admin)
    return response
  }

  const logout = () => {
    authService.logout()
    localStorage.removeItem('wilsy_token')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
