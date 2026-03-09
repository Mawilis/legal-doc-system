import api from '../api'

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/api/superadmin/login', { email, password })
    return response.data
  },

  logout: async () => {
    await api.post('/api/superadmin/logout')
  },

  getProfile: async () => {
    const response = await api.get('/api/superadmin/profile')
    return response.data
  },

  verifyMFA: async (code) => {
    const response = await api.post('/api/superadmin/verify-mfa', { code })
    return response.data
  }
}
