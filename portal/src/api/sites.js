import api from './base'

async function getSites(filters = {}) {
  const queryString = new URLSearchParams(filters).toString()

  try {
    const response = await api.get(`/sites?${queryString}`)
    const data = response.data
    return data
  } catch (error) {
    console.error('Error fetching sites:', error)
  }
}

async function getSitesFixed(filters = {}) {
  // Construir query params manualmente para manejar arrays (tags)
  const params = new URLSearchParams()
  
  Object.keys(filters).forEach(key => {
    const value = filters[key]
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        // Para arrays como tags, enviar como string separado por comas
        if (value.length > 0) {
          params.append(key, value.join(','))
        }
      } else {
        params.append(key, value)
      }
    }
  })

  try {
    const response = await api.get(`/sites/fix?${params.toString()}`)
    console.log('Response from /sites/fix:', response.data)
    const data = response.data
    return data
  } catch (error) {
    console.error('Error fetching sites:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
    throw error
  }
}

export { getSites, getSitesFixed }
