// src/api/base.js
import axios from 'axios'

/**
 * Instancia base de axios para hablar con la API de Flask.
 *
 * Ojo: esta instancia NO comparte headers automáticamente con axios global,
 * por eso abajo le agrego un interceptor para inyectar el JWT desde localStorage.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_API_URL || 'http://localhost:5000/api'
})

// Antes de cada request, si hay un JWT lo agrego como Authorization: Bearer <token>
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt')
    if (token) {
      config.headers = config.headers || {}
      if (!config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default api
