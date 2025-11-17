import api from './base'

async function getAllTags() {
  try {
    const response = await api.get('/tags')
    // El backend retorna { results: [...], total: ... }
    return response.data
  } catch (error) {
    console.error('Error fetching tags:', error)
    return { results: [], total: 0 }
  }
}

export { getAllTags }

