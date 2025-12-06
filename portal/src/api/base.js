// src/api/base.js
import axios from 'axios'

/**
 * Instancia base de axios para hablar con la API de Flask.
 *
 * Usamos la MISMA variable de entorno que el login (`useAuth`):
 *   VITE_API_BASE_URL
 *
 * Si no está definida, por defecto apuntamos a http://localhost:5000,
 * que es donde corre Flask en desarrollo.
 *
 * En main tiene que estar: 'https://admin-grupo45.proyecto2025.linti.unlp.edu.ar'
 */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'https://admin-grupo45.proyecto2025.linti.unlp.edu.ar'

const api = axios.create({
  // Todas las rutas de este cliente van contra /api del backend
  baseURL: `${API_BASE_URL}/api`,
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
  (error) => Promise.reject(error),
)

export default api
