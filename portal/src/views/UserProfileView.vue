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
              <p class="name">{{ displayName }}</p>
              <p class="email">{{ user?.email }}</p>
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
          <header class="list-header mb-4 sm:mb-6">
            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
              <div class="w-full sm:w-auto">
                <h1 class="text-lg sm:text-xl font-semibold text-gray-800 mb-1">Mis reseñas</h1>
              </div>
              <div class="flex flex-col-2 xs:flex-row gap-3 w-full sm:w-auto">
                <div class="relative filter-dropdown w-full xs:w-auto">
                  <!-- Menú desplegable de filtros -->
                  <transition
                    enter-active-class="transition duration-100 ease-out"
                    enter-from-class="transform scale-95 opacity-0"
                    enter-to-class="transform scale-100 opacity-100"
                    leave-active-class="transition duration-75 ease-in"
                    leave-from-class="transform scale-100 opacity-100"
                    leave-to-class="transform scale-95 opacity-0"
                  >
                  </transition>
                </div>
                
                <!-- Botón de orden -->
                <button 
                  class="order-btn px-3 sm:px-4 py-2 w-full xs:w-auto bg-white hover:bg-gray-50 rounded-lg border border-gray-300 text-xs sm:text-sm font-medium text-gray-700 shadow-sm transition-colors flex items-center justify-center xs:justify-start gap-1 sm:gap-2" 
                  @click="toggleReviewsOrder"
                >
                  <svg class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/>
                  </svg>
                  <span class="truncate">{{ reviewsOrderLabel }}</span>
                </button>
              </div>
            </div>
          </header>

          <!-- Estado de carga -->
          <div v-if="loadingReviews" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <p v-else-if="reviews.length === 0" class="empty text-center py-8 text-gray-500 text-sm sm:text-base">
            Aún no escribiste reseñas.
          </p>

          <ul v-else class="item-list space-y-4 sm:space-y-5">
            <li
              v-for="review in reviews"
              :key="review.id"
              class="item-card bg-white rounded-lg border border-gray-200 hover:border-gray-300 p-3 transition-all hover:shadow-sm"
            >
              <!-- Fila superior: Título, alias y rating -->
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-semibold text-gray-800 truncate">
                    {{ review.site_name }}
                  </h3>
                  <span class="text-xs px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-medium">
                    {{ displayName }}
                  </span>
                  <span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
                    {{ review.rating }}/5
                  </span>
                </div>
                <span class="text-xs text-gray-400">{{ formatDate(review.created_at) }}</span>
              </div>
              
              <!-- Fila media: Título y descripción -->
              <div class="mb-2">
                <p v-if="review.title" class="text-xs font-medium text-gray-700 mb-1">
                  {{ review.title }}
                </p>
                <p class="text-xs text-gray-600 line-clamp-2">
                  {{ review.body }}
                </p>
              </div>
              
              <!-- Fila inferior: Acciones -->
              <div class="flex items-center justify-between">
                <button 
                  @click="goToReviewSite(review)"
                  class="text-xs text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                  Ver sitio
                </button>
                
                <div class="flex items-center gap-2">
                  <!-- Estado -->
                  <span
                    v-if="review.status"
                    class="text-xs px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': review.status === 'approved',
                      'bg-yellow-100 text-yellow-800': review.status === 'pending',
                      'bg-red-100 text-red-800': review.status === 'rejected',
                    }"
                  >
                    {{ getStatusText(review.status) }}
                  </span>
                  
                  <!-- Menú de opciones -->
                  <button
                    type="button"
                    class="p-1 hover:bg-gray-100 rounded"
                    @click.stop="toggleReviewMenu(review.id)"
                  >
                    <svg class="w-3.5 h-3.5 text-gray-500" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </li>
          </ul>

          <!-- PAGINACIÓN -->
          <div v-if="reviews.length > 0" class="page-indicator mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
            <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
              <!-- Indicador de página -->
              <div class="flex items-center gap-2">
                <div class="flex items-center">
                  <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-l-lg text-sm font-medium">
                    Página
                  </span>
                  <span class="px-3 py-1 bg-blue-600 text-white text-sm font-medium">
                    {{ reviewsMeta.page }}
                  </span>
                  <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-r-lg text-sm font-medium">
                    de {{ Math.max(1, Math.ceil(reviewsMeta.total / reviewsMeta.per_page)) }}
                  </span>
                </div>
                
                <!-- Contador de reseñas -->
                <div class="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm">
                  {{ reviewsMeta.total }} reseña{{ reviewsMeta.total !== 1 ? 's' : '' }}
                </div>
              </div>
              
              <!-- Botones de navegación (solo si hay más de una página) -->
              <div v-if="reviewsMeta.total > reviewsMeta.per_page" class="flex items-center gap-2">
                <button
                  :disabled="reviewsMeta.page === 1"
                  @click="changeReviewsPage(reviewsMeta.page - 1)"
                  class="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Página anterior"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                  </svg>
                </button>
                <button
                  :disabled="reviewsMeta.page * reviewsMeta.per_page >= reviewsMeta.total"
                  @click="changeReviewsPage(reviewsMeta.page + 1)"
                  class="p-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Página siguiente"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- PESTAÑA DE FAVORITOS -->
        <section v-else class="list-section">
          <header class="list-header mb-4 sm:mb-6">
            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
              <div class="w-full sm:w-auto">
                <h2 class="text-lg sm:text-xl font-semibold text-gray-800 mb-1">Mis sitios favoritos</h2>
                <p class="text-xs sm:text-sm text-gray-500">Los sitios que marcaste como favoritos</p>
              </div>
              <button 
                class="order-btn px-3 sm:px-4 py-2 w-full sm:w-auto bg-white hover:bg-gray-50 rounded-lg border border-gray-300 text-xs sm:text-sm font-medium text-gray-700 shadow-sm transition-colors flex items-center justify-center sm:justify-start gap-1 sm:gap-2" 
                @click="toggleFavoritesOrder"
              >
                <svg class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"/>
                </svg>
                <span class="truncate">{{ favoritesOrderLabel }}</span>
              </button>
            </div>
          </header>

          <div v-if="loadingFavorites" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <p v-else-if="favorites.length === 0" class="empty text-center py-8 text-gray-500 text-sm sm:text-base">
            Aún no marcaste ningún sitio como favorito.
          </p>

          <ul v-else class="item-list grid gap-3 sm:gap-4 md:grid-cols-2">
            <li 
              v-for="fav in favorites" 
              :key="fav.site_id" 
              class="item-card bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-3 sm:p-4 hover:shadow-md transition-shadow"
            >
              <h3 class="item-title text-base sm:text-lg font-semibold text-gray-800 mb-1 sm:mb-2 line-clamp-2">
                {{ fav.site_name }}
              </h3>
              <div class="flex items-center text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4">
                <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                {{ formatDate(fav.created_at) }}
              </div>
              <button 
                @click="router.push({ name: 'site-detail', params: { id: fav.site_id } })"
                class="text-blue-600 hover:text-blue-800 text-xs sm:text-sm font-medium inline-flex items-center gap-1 transition-colors w-full sm:w-auto justify-center sm:justify-start"
              >
                Ver sitio
                <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                </svg>
              </button>
            </li>
          </ul>

          <!-- PAGINACIÓN DE FAVORITOS -->
          <div v-if="favoritesMeta.total > favoritesMeta.per_page" class="pager mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <button
                :disabled="favoritesMeta.page === 1"
                @click="changeFavoritesPage(favoritesMeta.page - 1)"
                class="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Anterior
              </button>
              <span class="text-xs sm:text-sm text-gray-600">
                Página <span class="font-semibold">{{ favoritesMeta.page }}</span>
              </span>
              <button
                :disabled="favoritesMeta.page * favoritesMeta.per_page >= favoritesMeta.total"
                @click="changeFavoritesPage(favoritesMeta.page + 1)"
                class="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Siguiente
              </button>
            </div>
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
import { fetchMyReviews, fetchMyFavorites, updateMyReview, deleteMyReview } from '@/api/profile'

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
const deleteReviewError = ref('') 

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

const changeFavoritesPage = (page) => {
  favoritesMeta.value.page = page
  loadFavorites()
}

// Gestión de menús
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

const confirmDeleteReview = async (review) => {
  closeReviewMenu()
  const ok = window.confirm(
    '¿Seguro que querés eliminar esta reseña? Esta acción no se puede deshacer.'
  )
  if (!ok) return

  deleteReviewError.value = ''
  try {
    await deleteMyReview(review.site_id, review.id)
    await loadReviews()
  } catch (error) {
    console.error('Error deleting review:', error)
    deleteReviewError.value = 'No se pudo eliminar la reseña. Intentá nuevamente.'
  }
}

// Función para texto del estado
const getStatusText = (status) => {
  const texts = {
    'approved': 'Aprobada',
    'pending': 'Pendiente',
    'rejected': 'Rechazada'
  }
  return texts[status] || status.charAt(0).toUpperCase() + status.slice(1)
}

const handleGlobalClick = (event) => {
  // Cerrar menú de acciones de reseña
  if (openReviewMenuId.value !== null) {
    const container = event.target.closest('[data-review-menu]')
    const activeId = String(openReviewMenuId.value)
    if (container && container.getAttribute('data-review-menu') === activeId) return
    closeReviewMenu()
  }
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
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'sites-list' })
  }
}

// Sistema de estrellas para edición
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

const selectReviewRating = (value) => {
  editReviewForm.rating = value
  hoverReviewRating.value = 0
}

const starPath = 'M22,9.81a1,1,0,0,0-.83-.69l-5.7-.78L12.88,3.53a1,1,0,0,0-1.76,0L8.57,8.34l-5.7.78a1,1,0,0,0-.82.69,1,1,0,0,0,.28,1l4.09,3.73-1,5.24A1,1,0,0,0,6.88,20.9L12,18.38l5.12,2.52a1,1,0,0,0,.44.1,1,1,0,0,0,1-1.18l-1-5.24,4.09-3.73A1,1,0,0,0,22,9.81Z'
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f3f4f6;
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
  gap: 0.5rem;
}

.item-card {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.item-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
</style>