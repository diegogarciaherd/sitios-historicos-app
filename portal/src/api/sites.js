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
  const params = new URLSearchParams()

  Object.keys(filters).forEach((key) => {
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

async function getSitesNearby({ lat, lng, radius, page, per_page, order_by, tags, city, province, search, favorites }) {
  // Reuse the main /sites endpoint so spatial + non-spatial filters are handled in one place.
  const params = { lat, lng, radius }
  if (page !== undefined) params.page = page
  if (per_page !== undefined) params.per_page = per_page
  if (order_by !== undefined) params.order_by = order_by
  if (tags !== undefined) params.tags = Array.isArray(tags) ? tags.join(',') : tags
  if (city !== undefined) params.city = city
  if (province !== undefined) params.province = province
  if (search !== undefined) params.search = search
  if (favorites !== undefined) params.favorites = favorites

  return api.get('/sites', {
    params,
    paramsSerializer: (p) => new URLSearchParams(p).toString(),
  })
}

async function getSiteCoverImage(siteId) {
  try {
    const response = await api.get(`/site_images/${siteId}/cover`)
    return response.data
  } catch (error) {
    console.error('Error fetching site cover image:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
  }
}

async function getSiteImages(siteId) {
  try {
    const response = await api.get(`/site_images/${siteId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching site images:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
  }
}

async function getSiteById(siteId) {
  try {
    const response = await api.get(`/sites/${siteId}`)
    return response.data
  } catch (error) {
    console.error('Error fetching site by ID:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
  }
}

async function getMostVisitedSites() {
  try {
    const response = await api.get('/sites/most_visited')
    return response.data
  } catch (error) {
    console.error('Error fetching most visited sites:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
  }
}

export {
  getSites,
  getSitesNearby,
  getSiteCoverImage,
  getSiteById,
  getSiteImages,
  getMostVisitedSites,
}
