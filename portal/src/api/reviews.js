// src/api/reviews.js
import api from './base'

/**
 * Trae las reseñas de un sitio.
 *
 * El backend devuelve:
 * {
 *   data: [ { id, title, body, rating, ... }, ... ],
 *   meta: { ... }
 * }
 *
 * Acá normalizo y devuelvo directamente el array de reseñas,
 * así el resto del código trabaja siempre con un array simple.
 */
export async function getSiteReviews (siteId) {
  const response = await api.get(`/sites/${siteId}/reviews`)
  const payload = response.data

  if (Array.isArray(payload)) {
    return payload
  }

  if (payload && Array.isArray(payload.data)) {
    return payload.data
  }

  return []
}

/**
 * Crea una reseña para un sitio.
 * params debe incluir al menos: { title, body, rating }
 */
export async function createSiteReview (siteId, params) {
  const response = await api.post(`/sites/${siteId}/reviews`, params)
  return response.data
}
