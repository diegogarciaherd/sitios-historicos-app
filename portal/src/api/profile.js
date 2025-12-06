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

export function fetchMyFavorites({
  page = 1,
  perPage = 25,
  order = 'desc',
  paginated = true,
} = {}) {
  return api.get('/sites/users/me/favorites', {
    params: {
      page,
      per_page: perPage,
      order,
      paginated: paginated ? 1 : undefined,
    },
  })
}

export function updateMyReview(reviewId, payload) {
  return api.post(`/sites/users/me/reviews/${reviewId}`, payload)
}

export function deleteMyReview(siteId, reviewId) {
  // usa el endpoint DELETE del back
  return api.delete(`/sites/${siteId}/reviews/${reviewId}`)
}
