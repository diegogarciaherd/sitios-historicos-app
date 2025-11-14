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

export { getSites }
