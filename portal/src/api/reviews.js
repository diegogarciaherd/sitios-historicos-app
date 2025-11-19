// src/api/reviews.js
import api from './base'

/**
 * Trae las reseñas de un sitio.
 */
export async function getSiteReviews(siteId) {
  const response = await api.get(`/sites/${siteId}/reviews`)
  // En tu backend puede venir como [reviews, meta] o directamente array; por ahora
  // asumimos array simple de reseñas. Si cambia el formato, se ajusta acá.
  return response.data
}

/**
 * Crea una reseña para un sitio.
 * params debe incluir al menos: { title, body, rating }
 */
export async function createSiteReview(siteId, params) {
  const response = await api.post(`/sites/${siteId}/reviews`, params)
  return response.data
}
