// src/api/profile.js
import api from './base'

export function fetchMyReviews({ page = 1, perPage = 25, order = 'desc' } = {}) {
  return api.get('/sites/users/me/reviews', {
    params: {
      page,
      per_page: perPage,
      order,
    },
  })
}

export function fetchMyFavorites({ page = 1, perPage = 25, order = 'desc', paginated = true } = {}) {
  return api.get('/sites/users/me/favorites', {
    params: {
      page,
      per_page: perPage,
      order,
      paginated: paginated ? 1 : undefined,
    },
  })
}
