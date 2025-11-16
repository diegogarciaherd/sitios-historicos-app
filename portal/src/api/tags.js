import api from './base'

async function getAllTags() {
  try {
    const response = await api.get('/tags/api?per_page=100')
    return response.data.results || []
  } catch (error) {
    console.error('Error fetching tags:', error)
    return []
  }
}

export { getAllTags }

