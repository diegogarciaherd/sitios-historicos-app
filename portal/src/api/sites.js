import api from './base'

/*
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
*/ 

async function getSites(filters = {}) {
  // Construir query params manualmente para manejar arrays (tags)
  console.log('📦 Filters recibidos en getSites:', filters)
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
    const response = await api.get(`/sites?${params.toString()}`)
    console.log('Response from /sites:', response.data)
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

async function getSitesNearby({ lat, lng, radius }) {
  return api.get("/sites/nearby", {
    params: {
      lat,
      lng,
      radius
    },
    paramsSerializer: params =>
      new URLSearchParams(params).toString()
  })
}

export { getSites, getSitesNearby }



