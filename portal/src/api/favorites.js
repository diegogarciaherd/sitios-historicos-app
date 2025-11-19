// src/api/favorites.js

import api from './base'

/**
 * Marca o desmarca un sitio como favorito para el usuario logueado.
 *
 * El backend hace el "toggle":
 * - si el favorito existía, lo borra
 * - si no existía, lo crea
 *
 * Devuelve algo del estilo:
 * {
 *   favorite: true | false,  // true si quedó como favorito
 *   site_id: number
 * }
 */
export async function toggleFavoriteRequest (siteId) {
  const response = await api.post(`/sites/${siteId}/favorite`)
  return response.data
}

/**
 * Trae todos los sitios que el usuario marcó como favoritos.
 *
 * La API responde con un array de objetos tipo:
 * [
 *   {
 *     site_id: number,
 *     site_name: string,
 *     created_at: string (ISO)
 *   },
 *   ...
 * ]
 */
export async function getMyFavoritesRequest () {
  const response = await api.get('/sites/users/me/favorites')
  return response.data
}
