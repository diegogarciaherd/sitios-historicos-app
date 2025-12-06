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
                <button class="order-btn px-3 sm:px-4 py-2 w-full xs:w-auto bg-white hover:bg-gray-50 rounded-lg border border-gray-300 text-xs sm:text-sm font-medium text-gray-700 shadow-sm transition-colors flex items-center justify-center xs:justify-start gap-1 sm:gap-2" @click="toggleReviewsOrder">
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
              class="item-card relative bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5 hover:shadow-md transition-shadow overflow-hidden"
              :data-review-menu="review.id"
            >
              <!-- BADGE DE ESTADO -->
              <span
                v-if="review.status"
                class="px-2 py-1 sm:px-3 sm:py-1.5 text-xs font-medium rounded-full text-white absolute top-3 right-3 sm:top-4 sm:right-4 z-10"
                :class="{
                  'bg-green-500': review.status === 'approved',
                  'bg-yellow-500': review.status === 'pending',
                  'bg-red-500': review.status === 'rejected',
                }"
              >
                {{ getStatusText(review.status) }}
              </span>
              
              <!-- Encabezado de la reseña -->
              <div class="item-header mb-3 sm:mb-4">
                <div class="pr-10 sm:pr-12">
                  <h3 class="item-title text-base sm:text-lg font-semibold text-gray-800 mb-1 line-clamp-1">
                    {{ review.site_name }}
                  </h3>
                  <div class="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-gray-500">
                    <span class="flex items-center gap-1">
                      <svg class="w-3 h-3 sm:w-4 sm:h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                      </svg>
                      {{ review.rating }}/5
                    </span>
                    <span class="hidden sm:inline">•</span>
                    <span class="text-gray-400 hidden sm:inline">|</span>
                    <span class="text-xs">{{ formatDate(review.created_at) }}</span>
                  </div>
                </div>
                <div
                  v-if="editingReviewId !== review.id"
                  class="review-actions absolute top-3 right-3 sm:static sm:top-auto sm:right-auto"
                >
                  <button
                    type="button"
                    class="menu-trigger p-1 sm:p-2 hover:bg-gray-100 rounded-full transition-colors"
                    @click.stop="toggleReviewMenu(review.id)"
                    aria-haspopup="true"
                    :aria-expanded="openReviewMenuId === review.id"
                  >
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                    </svg>
                  </button>
                  <div v-if="openReviewMenuId === review.id" class="menu-panel" role="menu">
                    <button
                      type="button"
                      class="menu-item"
                      role="menuitem"
                      @click.stop="startEditingReview(review)"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                      <span class="text-xs sm:text-sm">Editar reseña</span>
                    </button>
                    <button
                      type="button"
                      class="menu-item"
                      role="menuitem"
                      @click.stop="goToReviewSite(review)"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                      <span class="text-xs sm:text-sm">Ver sitio</span>
                    </button>
                    <button
                      type="button"
                      class="menu-item text-red-600 hover:bg-red-50"
                      role="menuitem"
                      @click.stop="confirmDeleteReview(review)"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                      <span class="text-xs sm:text-sm">Eliminar reseña</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- CONTENIDO DE LA RESEÑA O FORMULARIO DE EDICIÓN -->
              <div v-if="editingReviewId === review.id" class="edit-review-form mt-4 pt-4 border-t border-gray-100">
                <form @submit.prevent="submitReviewEdit(review)">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        Título
                      </label>
                      <input
                        v-model="editReviewForm.title"
                        type="text"
                        class="w-full px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                        placeholder="Escribe un título para tu reseña"
                        maxlength="120"
                        required
                      />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        Descripción
                      </label>
                      <textarea
                        v-model="editReviewForm.body"
                        class="w-full px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-y min-h-[100px]"
                        rows="4"
                        placeholder="Describe tu experiencia en este sitio..."
                        required
                      ></textarea>
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-3">
                        Calificación
                      </label>
                      <div class="review-rating-picker flex items-center gap-1">
                        <button
                          v-for="star in interactiveReviewStars"
                          :key="star.value"
                          type="button"
                          class="review-rating-button p-0.5 sm:p-1 hover:scale-110 transition-transform"
                          :class="{ 'filled': star.filled }"
                          @click="selectReviewRating(star.value)"
                          @mouseenter="hoverReviewRating = star.value"
                          @mouseleave="hoverReviewRating = 0"
                        >
                          <svg viewBox="0 0 24 24" class="review-rating-icon w-6 h-6 sm:w-8 sm:h-8">
                            <path
                              :d="starPath"
                              :fill="star.filled ? '#f59e0b' : '#e5e7eb'"
                            />
                          </svg>
                        </button>
                        <span class="ml-2 sm:ml-3 text-sm font-medium text-gray-700">
                          {{ editReviewForm.rating }} / 5
                        </span>
                      </div>
                    </div>
                    
                    <div v-if="editReviewError" class="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p class="text-sm text-red-600 flex items-center gap-2">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                        {{ editReviewError }}
                      </p>
                    </div>
                    
                    <div class="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 pt-2">
                      <button
                        type="button"
                        class="px-4 sm:px-5 py-2 sm:py-2.5 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg border border-gray-300 transition-colors w-full sm:w-auto"
                        @click="cancelEditingReview"
                      >
                        Cancelar
                      </button>
                      <button
                        type="submit"
                        class="px-4 sm:px-5 py-2 sm:py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 w-full sm:w-auto"
                        :disabled="savingReview"
                      >
                        <svg v-if="savingReview" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {{ savingReview ? 'Guardando...' : 'Guardar cambios' }}
                      </button>
                    </div>
                  </div>
                </form>
              </div>
              
              <div v-else class="review-body">
                <div class="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-100">
                  <p v-if="review.title" class="text-sm sm:text-base font-semibold text-gray-800 mb-2 sm:mb-3 line-clamp-2">
                    {{ review.title }}
                  </p>
                  <p class="text-gray-600 leading-relaxed text-sm sm:text-base break-words whitespace-pre-line max-h-32 sm:max-h-48 overflow-y-auto pr-2">
                    {{ review.body }}
                  </p>
                </div>
              </div>
            </li>
          </ul>

          <!-- PAGINACIÓN -->
          <div v-if="reviewsMeta.total > reviewsMeta.per_page" class="pager mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
            <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                :disabled="reviewsMeta.page === 1"
                @click="changeReviewsPage(reviewsMeta.page - 1)"
                class="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1 sm:gap-2 w-full sm:w-auto justify-center"
              >
                <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                Anterior
              </button>
              
              <div class="text-xs sm:text-sm text-gray-600 text-center">
                <span class="font-semibold">{{ reviewsMeta.page }}</span> de 
                <span class="font-semibold">{{ Math.ceil(reviewsMeta.total / reviewsMeta.per_page) }}</span>
                <span class="mx-1 sm:mx-2 hidden xs:inline">•</span>
                <span class="text-gray-500 block xs:inline mt-1 xs:mt-0">{{ reviewsMeta.total }} reseñas</span>
              </div>
              
              <button
                :disabled="reviewsMeta.page * reviewsMeta.per_page >= reviewsMeta.total"
                @click="changeReviewsPage(reviewsMeta.page + 1)"
                class="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1 sm:gap-2 w-full sm:w-auto justify-center"
              >
                Siguiente
                <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
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
              <button class="order-btn px-3 sm:px-4 py-2 w-full sm:w-auto bg-white hover:bg-gray-50 rounded-lg border border-gray-300 text-xs sm:text-sm font-medium text-gray-700 shadow-sm transition-colors flex items-center justify-center sm:justify-start gap-1 sm:gap-2" @click="toggleFavoritesOrder">
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
            <li v-for="fav in favorites" :key="fav.site_id" class="item-card bg-white rounded-lg sm:rounded-xl shadow-sm border border-gray-200 p-3 sm:p-4 hover:shadow-md transition-shadow">
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
