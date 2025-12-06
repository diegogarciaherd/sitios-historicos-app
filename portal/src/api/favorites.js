// src/api/favorites.js
import api from './base'

/**
 * Alterna el estado de favorito de un sitio.
 * Devuelve el JSON que envíe el backend, por ejemplo:
 *   { favorite: true/false, site_id }
 */
export async function toggleFavoriteRequest (siteId) {
  const response = await api.post(`/sites/${siteId}/favorite`)
  return response.data
}

/**
 * Devuelve la lista de favoritos del usuario autenticado.
 *
 * El backend devuelve un array de objetos con al menos:
 *   [{ site_id, site_name, created_at }, ...]
 */
export async function getMyFavoritesRequest () {
  const response = await api.get('/sites/users/me/favorites')
  return response.data
}
