import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.BASE_URL || 'http://localhost:5000/api',
})

export default api
