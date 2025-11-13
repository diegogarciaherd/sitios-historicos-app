import api from './base'

async function getSites(filters = {}) {
  try {
    const response = await api.get('/sites/', {
      filters: { ...filters },
    })
    const data = response.data
    return data
  } catch (error) {
    console.error('Error fetching sites:', error)
  }
}

export { getSites }
