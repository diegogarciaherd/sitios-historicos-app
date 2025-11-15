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
  const queryString = new URLSearchParams(filters).toString()

  try {
    const response = await api.get(`/sites/fix?${queryString}`)
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
