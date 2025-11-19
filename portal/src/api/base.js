import axios from 'axios'

const api = axios.create({
  baseURL: 'https://admin-grupo45.proyecto2025.linti.unlp.edu.ar/api',
})

export default api
