import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_API_URL || 'http://localhost:5000/api',
})

// Interceptor para agregar JWT token si está disponible
api.interceptors.request.use(
  (config) => {
    // Intentar obtener el token de localStorage o sessionStorage
    const token = localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api
