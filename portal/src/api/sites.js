import api from './base'

async function getSites(filters = {}) {
  const queryString = new URLSearchParams(filters).toString()

  try {
    const response = await fetch(`http://localhost:5000/api/sites?${queryString}`)
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching sites:', error)
  }
}

export { getSites }
