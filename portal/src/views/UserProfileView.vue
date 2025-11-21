<template>
  <div class="profile-page">
    <!-- Topbar global -->
    <Topbar />

    <main class="profile-container">
      <section class="profile-card">
        <!-- Cabecera de perfil -->
        <header class="profile-header">
          <div class="profile-header-left">
            <div class="avatar">
              <span>{{ initials }}</span>
            </div>
            <div class="user-info">
              <p class="name">
                {{ displayName }}
              </p>
              <p class="email">
                {{ user?.email }}
              </p>
            </div>
          </div>

          <button class="back-button" type="button" @click="goBack">← Volver</button>
        </header>

        <!-- Pestañas -->
        <nav class="tabs">
          <span class="tabs-indicator" :style="tabIndicatorStyle" aria-hidden="true"></span>
          <button :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
            Mis reseñas
          </button>
          <button :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">
            Mis favoritos
          </button>
        </nav>

        <!-- Contenido de pestañas -->
        <section v-if="activeTab === 'reviews'" class="list-section">
          <header class="list-header">
            <h2>Mis reseñas</h2>
            <button class="order-btn" @click="toggleReviewsOrder">
              Orden: {{ reviewsOrderLabel }}
            </button>
          </header>

          <p v-if="!loadingReviews && reviews.length === 0" class="empty">
            Aún no escribiste reseñas.
          </p>

          <ul v-else class="item-list">
            <li
              v-for="review in reviews"
              :key="review.id"
              class="item-card"
              :data-review-menu="review.id"
            >
              <span
                class="px-1.5 py-0.5 text-xs rounded-full text-white absolute top-3 right-3"
                :class="{
                  'bg-green-400': review.status === 'approved',
                  'bg-yellow-600': review.status === 'pending',
                  'bg-red-600': review.status === 'rejected',
                }"
              >
                {{ review.status }}
              </span>
              <div class="item-header">
                <div>
                  <h3 class="item-title">{{ review.site_name }}</h3>
                  <p class="meta">{{ formatDate(review.created_at) }} · ★ {{ review.rating }}</p>
                </div>
                <div
                  v-if="editingReviewId !== review.id"
                  class="review-actions h-[80%] flex items-center"
                >
                  <button
                    type="button"
                    class="menu-trigger"
                    @click.stop="toggleReviewMenu(review.id)"
                    aria-haspopup="true"
                    :aria-expanded="openReviewMenuId === review.id"
                  >
                    <svg
                      viewBox="0 0 16 16"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="#000000"
                      class="w-4 h-4"
                    >
                      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                      <g
                        id="SVGRepo_tracerCarrier"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      ></g>
                      <g id="SVGRepo_iconCarrier">
                        <path
                          d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"
                        ></path>
                      </g>
                    </svg>
                  </button>
                  <div v-if="openReviewMenuId === review.id" class="menu-panel" role="menu">
                    <button
                      type="button"
                      class="menu-item"
                      role="menuitem"
                      @click.stop="startEditingReview(review)"
                    >
                      Editar reseña
                    </button>
                    <button
                      type="button"
                      class="menu-item"
                      role="menuitem"
                      @click.stop="goToReviewSite(review)"
                    >
                      Ver sitio
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="editingReviewId === review.id" class="edit-review-form">
                <form @submit.prevent="submitReviewEdit(review)">
                  <label class="form-label">
                    Título
                    <input
                      v-model="editReviewForm.title"
                      type="text"
                      class="form-input"
                      placeholder="Mi experiencia"
                      maxlength="120"
                      required
                    />
                  </label>
                  <label class="form-label">
                    Detalle
                    <textarea
                      v-model="editReviewForm.body"
                      class="form-textarea"
                      rows="4"
                      placeholder="Contanos cómo fue tu visita"
                      required
                    ></textarea>
                  </label>
                  <div>
                    <label class="flex items-center gap-2 text-xs mb-1">
                      Calificación
                      <span class="text-[0.7rem] text-slate-400"
                        >{{ editReviewForm.rating }} / 5</span
                      >
                    </label>
                    <div
                      class="review-rating-picker"
                      role="radiogroup"
                      :aria-label="reviewRatingAria"
                    >
                      <button
                        v-for="star in interactiveReviewStars"
                        :key="star.value"
                        type="button"
                        class="review-rating-button"
                        :class="{ filled: star.filled }"
                        role="radio"
                        :aria-checked="editReviewForm.rating === star.value"
                        :aria-label="star.label"
                        @click="selectReviewRating(star.value)"
                        @mouseenter="hoverReviewRating = star.value"
                        @mouseleave="hoverReviewRating = 0"
                        @focus="hoverReviewRating = star.value"
                        @blur="hoverReviewRating = 0"
                        @keydown="handleReviewStarKeydown($event, star.value)"
                      >
                        <svg viewBox="0 0 24 24" class="review-rating-icon" aria-hidden="true">
                          <path
                            :d="starPath"
                            :fill="star.filled ? '#facc15' : 'rgba(148, 163, 184, 0.3)'"
                          />
                          <path
                            :d="starPath"
                            fill="none"
                            stroke="#facc15"
                            stroke-width="1.2"
                            stroke-linejoin="round"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <p v-if="editReviewError" class="form-error">{{ editReviewError }}</p>
                  <div class="form-actions">
                    <button type="button" class="btn-secondary" @click="cancelEditingReview">
                      Cancelar
                    </button>
                    <button type="submit" class="btn-primary" :disabled="savingReview">
                      {{ savingReview ? 'Guardando…' : 'Guardar cambios' }}
                    </button>
                  </div>
                </form>
              </div>
              <div v-else class="review-body">
                <p v-if="review.title" class="text-lg">{{ review.title }}</p>
                <p class="text-sm">
                  {{ review.body }}
                </p>
              </div>
            </li>
          </ul>

          <div v-if="reviewsMeta.total > reviewsMeta.per_page" class="pager">
            <button
              :disabled="reviewsMeta.page === 1"
              @click="changeReviewsPage(reviewsMeta.page - 1)"
            >
              Anterior
            </button>
            <span>Página {{ reviewsMeta.page }}</span>
            <button
              :disabled="reviewsMeta.page * reviewsMeta.per_page >= reviewsMeta.total"
              @click="changeReviewsPage(reviewsMeta.page + 1)"
            >
              Siguiente
            </button>
          </div>
        </section>

        <section v-else class="list-section">
          <header class="list-header">
            <h2>Mis sitios favoritos</h2>
            <button class="order-btn" @click="toggleFavoritesOrder">
              Orden: {{ favoritesOrderLabel }}
            </button>
          </header>

          <p v-if="!loadingFavorites && favorites.length === 0" class="empty">
            Aún no marcaste ningún sitio como favorito.
          </p>

          <ul v-else class="item-list">
            <li v-for="fav in favorites" :key="fav.site_id" class="item-card">
              <h3 class="item-title">{{ fav.site_name }}</h3>
              <p class="meta">
                {{ formatDate(fav.created_at) }}
              </p>
            </li>
          </ul>

          <div v-if="favoritesMeta.total > favoritesMeta.per_page" class="pager">
            <button
              :disabled="favoritesMeta.page === 1"
              @click="changeFavoritesPage(favoritesMeta.page - 1)"
            >
              Anterior
            </button>
            <span>Página {{ favoritesMeta.page }}</span>
            <button
              :disabled="favoritesMeta.page * favoritesMeta.per_page >= favoritesMeta.total"
              @click="changeFavoritesPage(favoritesMeta.page + 1)"
            >
              Siguiente
            </button>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, reactive } from 'vue'
import { useRouter } from 'vue-router'
import Topbar from '@/components/TopbarPhone.vue'
import { useAuth } from '@/composables/useAuth'
import { fetchMyReviews, fetchMyFavorites, updateMyReview } from '@/api/profile'

const router = useRouter()
const { currentUser, isAuthenticated } = useAuth()

const user = computed(() => currentUser.value)

const activeTab = ref('reviews')

const tabIndicatorStyle = computed(() => {
  const index = activeTab.value === 'favorites' ? 1 : 0
  return {
    transform: `translateX(${index * 100}%)`,
  }
})

// RESEÑAS
const reviews = ref([])
const reviewsMeta = ref({ page: 1, per_page: 25, total: 0 })
const reviewsOrder = ref('desc')
const loadingReviews = ref(false)
const openReviewMenuId = ref(null)
const editingReviewId = ref(null)
const editReviewForm = reactive({
  title: '',
  body: '',
  rating: 5,
})
const editReviewError = ref('')
const savingReview = ref(false)

// FAVORITOS
const favorites = ref([])
const favoritesMeta = ref({ page: 1, per_page: 25, total: 0 })
const favoritesOrder = ref('desc')
const loadingFavorites = ref(false)

const hoverReviewRating = ref(0)

// Carga
const loadReviews = async () => {
  loadingReviews.value = true
  try {
    const { data } = await fetchMyReviews({
      page: reviewsMeta.value.page,
      perPage: reviewsMeta.value.per_page,
      order: reviewsOrder.value,
    })
    reviews.value = data.data
    reviewsMeta.value = data.meta
  } finally {
    loadingReviews.value = false
    openReviewMenuId.value = null
    editingReviewId.value = null
    editReviewError.value = ''
  }
}

const loadFavorites = async () => {
  loadingFavorites.value = true
  try {
    const { data } = await fetchMyFavorites({
      page: favoritesMeta.value.page,
      perPage: favoritesMeta.value.per_page,
      order: favoritesOrder.value,
    })
    favorites.value = data.data
    favoritesMeta.value = data.meta
  } finally {
    loadingFavorites.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleGlobalClick)

  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }

  await loadReviews()
  await loadFavorites()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleGlobalClick)
})

// Orden
const toggleReviewsOrder = () => {
  reviewsOrder.value = reviewsOrder.value === 'desc' ? 'asc' : 'desc'
  reviewsMeta.value.page = 1
  loadReviews()
}

const toggleFavoritesOrder = () => {
  favoritesOrder.value = favoritesOrder.value === 'desc' ? 'asc' : 'desc'
  favoritesMeta.value.page = 1
  loadFavorites()
}

const reviewsOrderLabel = computed(() =>
  reviewsOrder.value === 'desc' ? 'Más nuevas primero' : 'Más antiguas primero',
)

const favoritesOrderLabel = computed(() =>
  favoritesOrder.value === 'desc' ? 'Más nuevos primero' : 'Más antiguos primero',
)

// Paginación
const changeReviewsPage = (page) => {
  reviewsMeta.value.page = page
  loadReviews()
}

const toggleReviewMenu = (reviewId) => {
  openReviewMenuId.value = openReviewMenuId.value === reviewId ? null : reviewId
}

const closeReviewMenu = () => {
  openReviewMenuId.value = null
}

const goToReviewSite = (review) => {
  if (review?.site_id) {
    router.push({ name: 'site-detail', params: { id: review.site_id } })
  }
  closeReviewMenu()
}

const startEditingReview = (review) => {
  editReviewError.value = ''
  editReviewForm.title = review.title ?? ''
  editReviewForm.body = review.body ?? review.excerpt ?? ''
  const parsedRating = Number(review.rating ?? 5)
  editReviewForm.rating = Number.isFinite(parsedRating) && parsedRating >= 1 ? parsedRating : 5
  editingReviewId.value = review.id
  closeReviewMenu()
}

const cancelEditingReview = () => {
  editingReviewId.value = null
  editReviewError.value = ''
  editReviewForm.title = ''
  editReviewForm.body = ''
  editReviewForm.rating = 5
  closeReviewMenu()
}

const submitReviewEdit = async (review) => {
  if (!editingReviewId.value) return
  savingReview.value = true
  editReviewError.value = ''
  try {
    await updateMyReview(review.id, {
      title: editReviewForm.title.trim(),
      body: editReviewForm.body.trim(),
      rating: editReviewForm.rating,
    })
    await loadReviews()
    editReviewForm.title = ''
    editReviewForm.body = ''
    editReviewForm.rating = 5
  } catch (error) {
    console.error('Error updating review:', error)
    editReviewError.value = 'No se pudo actualizar la reseña. Intentá nuevamente.'
  } finally {
    savingReview.value = false
  }
}

const handleGlobalClick = (event) => {
  if (openReviewMenuId.value === null) return
  const container = event.target.closest('[data-review-menu]')
  const activeId = String(openReviewMenuId.value)
  if (container && container.getAttribute('data-review-menu') === activeId) return
  closeReviewMenu()
}

const changeFavoritesPage = (page) => {
  favoritesMeta.value.page = page
  loadFavorites()
}

// Utilidades UI
const formatDate = (isoString) =>
  new Date(isoString).toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })

const initials = computed(() => {
  if (!user.value) return ''
  const full = `${user.value.name || ''} ${user.value.last_name || ''}`.trim()
  if (!full) return (user.value.email || '?')[0].toUpperCase()
  return full
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
})

const displayName = computed(() => {
  if (!user.value) return 'Usuario'
  const full = `${user.value.name || ''} ${user.value.last_name || ''}`.trim()
  return full || 'Usuario'
})

const goBack = () => {
  // si venís desde otro lado vuelve en el history, si no te manda a /sitios
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'sites-list' })
  }
}

const ratingStars = computed(() => {
  return Array.from({ length: 5 }, (_, index) => {
    const value = averageRating.value - index
    if (value >= 1) return 100
    if (value <= 0) return 0
    return Math.round(value * 100)
  })
})

const ratingAriaLabel = computed(() => {
  const count = ratingCount.value
  if (!count) return 'Sin reseñas registradas'
  const plural = count === 1 ? 'reseña' : 'reseñas'
  return `Puntuación promedio ${averageRating.value.toFixed(1)} de 5 basada en ${count} ${plural}`
})

const interactiveReviewStars = computed(() => {
  const display = hoverReviewRating.value || editReviewForm.rating
  return Array.from({ length: 5 }, (_, index) => {
    const value = index + 1
    return {
      value,
      filled: value <= display,
      label: `${value} estrella${value > 1 ? 's' : ''}`,
    }
  })
})

const reviewRatingAria = computed(() => {
  const value = editReviewForm.rating
  return `Puntaje seleccionado: ${value} estrella${value === 1 ? '' : 's'}`
})

const selectReviewRating = (value) => {
  editReviewForm.rating = value
  hoverReviewRating.value = 0
}

const handleReviewStarKeydown = (event, value) => {
  if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
    event.preventDefault()
    const nextValue = Math.min(5, value + 1)
    selectReviewRating(nextValue)
    requestAnimationFrame(() => {
      event.currentTarget?.nextElementSibling?.focus()
    })
    return
  }

  if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
    event.preventDefault()
    const prevValue = Math.max(1, value - 1)
    selectReviewRating(prevValue)
    requestAnimationFrame(() => {
      event.currentTarget?.previousElementSibling?.focus()
    })
    return
  }

  if (event.key === 'Home') {
    event.preventDefault()
    selectReviewRating(1)
    requestAnimationFrame(() => {
      event.currentTarget?.parentElement?.firstElementChild?.focus()
    })
    return
  }

  if (event.key === 'End') {
    event.preventDefault()
    selectReviewRating(5)
    requestAnimationFrame(() => {
      event.currentTarget?.parentElement?.lastElementChild?.focus()
    })
    return
  }

  if (event.key === ' ' || event.key === 'Spacebar' || event.key === 'Enter') {
    event.preventDefault()
    selectReviewRating(value)
  }
}

const starPath =
  'M22,9.81a1,1,0,0,0-.83-.69l-5.7-.78L12.88,3.53a1,1,0,0,0-1.76,0L8.57,8.34l-5.7.78a1,1,0,0,0-.82.69,1,1,0,0,0,.28,1l4.09,3.73-1,5.24A1,1,0,0,0,6.88,20.9L12,18.38l5.12,2.52a1,1,0,0,0,.44.1,1,1,0,0,0,1-1.18l-1-5.24,4.09-3.73A1,1,0,0,0,22,9.81Z'
const starUid = Math.random().toString(36).slice(2, 8)
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f3f4f6; /* gris clarito */
}

/* contenedor general */
.profile-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1rem 2rem;
}

/* tarjeta principal */
.profile-card {
  background: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
  padding: 1.5rem 1.75rem 2rem;
}

/* cabecera */
.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.profile-header-left {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #60a5fa, #1e40af);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f9fafb;
  font-weight: 600;
  font-size: 1.1rem;
}

.user-info .name {
  font-weight: 600;
  font-size: 1.05rem;
  margin: 0;
}

.user-info .email {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0.1rem 0 0;
}

.back-button {
  border: none;
  background: transparent;
  font-size: 0.85rem;
  color: #2563eb;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.back-button:hover {
  text-decoration: underline;
}

/* pestañas */
.tabs {
  position: relative;
  display: flex;
  border-radius: 999px;
  background: #e5e7eb;
  padding: 0.25rem;
  margin-bottom: 1.25rem;
  overflow: hidden;
}

.tabs button {
  flex: 1;
  border: none;
  background: transparent;
  color: #4b5563;
  padding: 0.5rem 0.75rem;
  border-radius: 999px;
  font-size: 0.9rem;
  cursor: pointer;
  position: relative;
  z-index: 1;
  transition: color 220ms ease;
}

.tabs button.active {
  color: #ffffff;
}

.tabs-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border-radius: 999px;
  transform: translateX(0);
  transition: transform 320ms ease;
  box-shadow: 0 12px 30px rgba(37, 99, 235, 0.25);
}

/* contenido */
.list-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-header h2 {
  font-size: 1rem;
  margin: 0;
}

.order-btn {
  font-size: 0.8rem;
  border: none;
  background: transparent;
  color: #2563eb;
  cursor: pointer;
}

.empty {
  font-size: 0.9rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item-card {
  padding: 0.85rem 0.9rem;
  border-radius: 0.75rem;
  background: #f9fafb;
  position: relative;
}

.item-title {
  margin: 0 0 0.25rem;
  font-size: 0.98rem;
}

.meta {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.review-actions {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
}

.item-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.item-header > div:first-child {
  flex: 1;
}

.review-body {
  margin-top: 0.6rem;
  display: grid;
  gap: 0.35rem;
}

.edit-review-form {
  margin-top: 0.75rem;
}

.edit-review-form form {
  display: grid;
  gap: 0.6rem;
}

.form-label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: #4b5563;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  border-radius: 0.6rem;
  border: 1px solid #d1d5db;
  padding: 0.55rem 0.7rem;
  font-size: 0.9rem;
  background: #ffffff;
  transition: border-color 180ms ease;
}

.form-textarea {
  resize: vertical;
  min-height: 130px;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.btn-primary,
.btn-secondary {
  border-radius: 999px;
  padding: 0.45rem 1.05rem;
  font-size: 0.85rem;
  border: none;
  cursor: pointer;
  transition: background 180ms ease;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #ffffff;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: default;
}

.btn-secondary {
  background: #e5e7eb;
  color: #1f2937;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.form-error {
  color: #dc2626;
  font-size: 0.8rem;
}

.menu-trigger {
  width: 1.75rem;
  height: 1.75rem;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #6b7280;
  font-size: 1.1rem;
  cursor: pointer;
  transition:
    background 180ms ease,
    color 180ms ease;
}

.menu-trigger:hover,
.menu-trigger:focus-visible {
  background: rgba(148, 163, 184, 0.25);
  color: #1f2937;
  outline: none;
}

.menu-panel {
  position: absolute;
  top: 3.5rem;
  right: 0;
  width: 176px;
  padding: 0.35rem 0;
  border-radius: 0.75rem;
  background: #ffffff;
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(148, 163, 184, 0.25);
  z-index: 15;
}

.menu-item {
  width: 100%;
  padding: 0.45rem 0.85rem;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 0.85rem;
  color: #1f2937;
  cursor: pointer;
  transition:
    background 160ms ease,
    color 160ms ease;
}

.menu-item:hover,
.menu-item:focus-visible {
  background: rgba(59, 130, 246, 0.12);
  color: #1d4ed8;
  outline: none;
}

/* paginador */
.pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.9rem;
  font-size: 0.85rem;
}

.pager button {
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  padding: 0.3rem 0.8rem;
  cursor: pointer;
}

.pager button:disabled {
  opacity: 0.4;
  cursor: default;
}

@media (max-width: 640px) {
  .profile-card {
    padding-inline: 1.25rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .back-button {
    align-self: flex-end;
  }
}

.review-rating-picker {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.review-rating-button {
  width: 2.25rem;
  height: 2.25rem;
  border: none;
  border-radius: 999px;
  background: transparent;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition:
    transform 150ms ease,
    background 150ms ease;
}

.review-rating-button:hover,
.review-rating-button:focus-visible {
  background: rgba(56, 189, 248, 0.12);
  outline: none;
}

.review-rating-button.filled .review-rating-icon {
  transform: scale(1.05);
}

.review-rating-icon {
  width: 1.6rem;
  height: 1.6rem;
  transition: transform 150ms ease;
}
</style>
