<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Topbar from '@/components/TopbarPhone.vue'
import { getSiteById, getSiteCoverImage, getSiteImages } from '@/api/sites'
import { getSiteReviews, createSiteReview } from '@/api/reviews'
import { toggleFavoriteRequest, getMyFavoritesRequest } from '@/api/favorites'
import { useAuth } from '@/composables/useAuth'
import SiteViewCarousel from '@/components/SiteViewCarousel.vue'
import SiteMap from '@/components/SiteMap.vue'
import Tag from '@/components/Tag.vue'

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()

const siteId = computed(() => Number(route.params.id))

// Estado del sitio
const site = ref(null)
const loadingSite = ref(true)
const siteError = ref('')
const showFullDescription=ref(false)

// Imágenes
const coverImage = ref(null)
const siteImages = ref([])
const loadingImages = ref(false)

// Favoritos
const isFavorite = ref(false)
const loadingFavorite = ref(false)

// Reseñas
const reviews = ref([])
const loadingReviews = ref(false)
const hasReviews = computed(() => reviews.value.length > 0)

const newReviewTitle = ref('')
const newReviewBody = ref('')
const newReviewRating = ref(5)
const hoverReviewRating = ref(0)
const creatingReview = ref(false)
const createReviewError = ref('')
const showSuccessMessage = ref(false)
const reviewSubmissionError = ref('') // Para errores de backend (como "ya tiene reseña")


// errores de validación en el front
const newReviewTitleError = ref('')
const newReviewBodyError = ref('')
const newReviewRatingError = ref('')

const averageRating = computed(() => {
  if (!site.value || !site.value.cantidadResenas) return 0
  const total = Number(site.value.puntuacionTotal) || 0
  const count = Number(site.value.cantidadResenas) || 0
  if (!count) return 0
  const avg = total / count
  if (!Number.isFinite(avg)) return 0
  return Math.min(5, Math.max(0, avg))
})

const ratingCount = computed(() => {
  if (!site.value) return 0
  const count = Number(site.value.cantidadResenas)
  return Number.isFinite(count) && count > 0 ? count : 0
})

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
  const display = hoverReviewRating.value || newReviewRating.value
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
  const value = newReviewRating.value
  return `Puntaje seleccionado: ${value} estrella${value === 1 ? '' : 's'}`
})

const canSubmitReview = computed(() => {
  return isAuthenticated.value && !creatingReview.value
})

const selectReviewRating = (value) => {
  newReviewRating.value = value
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

/**
 * Carga los datos del sitio.
 */
async function loadSite() {
  loadingSite.value = true
  siteError.value = ''
  try {
    const data = await getSiteById(siteId.value)
    site.value = data || null
    coverImage.value = await getSiteCoverImage(siteId.value)
  } catch (error) {
    console.error('Error cargando sitio:', error)
    siteError.value = 'No se pudo cargar la información del sitio.'
  } finally {
    loadingSite.value = false
  }
}

/**
 * Carga las imágenes del sitio.
 */
async function loadImages() {
  loadingImages.value = true
  try {
    const images = await getSiteImages(siteId.value)
    const coverImage = await getSiteCoverImage(siteId.value)
    site.value.image = coverImage
    siteImages.value = images || []
  } catch (error) {
    console.error('Error cargando imágenes del sitio:', error)
  } finally {
    loadingImages.value = false
  }
}

/**
 * Carga el estado de favorito para este sitio.
 */
async function loadFavoriteState() {
  if (!isAuthenticated.value) {
    isFavorite.value = false
    return
  }

  try {
    const favs = await getMyFavoritesRequest()
    if (Array.isArray(favs)) {
      isFavorite.value = favs.some((f) => f.site_id === siteId.value)
    }
  } catch (error) {
    console.error('Error cargando estado de favorito:', error)
  }
}

/**
 * Alterna el favorito del sitio actual.
 */
async function handleToggleFavorite() {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }

  loadingFavorite.value = true
  try {
    const data = await toggleFavoriteRequest(siteId.value)
    if (typeof data.favorite === 'boolean') {
      isFavorite.value = data.favorite
    } else {
      // Fallback por si algún día cambia el backend
      isFavorite.value = !isFavorite.value
    }
  } catch (error) {
    console.error('Error alternando favorito:', error)
  } finally {
    loadingFavorite.value = false
  }
}

/**
 * Carga las reseñas del sitio.
 */
async function loadReviews() {
  loadingReviews.value = true
  try {
    const data = await getSiteReviews(siteId.value)
    reviews.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error cargando reseñas:', error)
  } finally {
    loadingReviews.value = false
  }
}

/**
 * Crea una nueva reseña para este sitio.
 * Incluye validaciones en el front y manejo de errores del backend.
 */
async function handleCreateReview() {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }

  // Limpiar todos los mensajes previos
  createReviewError.value = ''
  reviewSubmissionError.value = ''
  showSuccessMessage.value = false
  newReviewTitleError.value = ''
  newReviewBodyError.value = ''
  newReviewRatingError.value = ''

  const title = (newReviewTitle.value || '').trim()
  const body = (newReviewBody.value || '').trim()
  const rating = Number(newReviewRating.value)

  let hasError = false

  // Validaciones que reflejan las del backend
  // Título: obligatorio, máx. 120
  if (!title) {
    newReviewTitleError.value = 'El título es obligatorio.'
    hasError = true
  } else if (title.length > 120) {
    newReviewTitleError.value = 'El título no puede superar los 120 caracteres.'
    hasError = true
  }

  // Descripción: obligatoria, entre 20 y 1000
  if (!body) {
    newReviewBodyError.value = 'La descripción es obligatoria.'
    hasError = true
  } else if (body.length < 20) {
    newReviewBodyError.value = 'La descripción debe tener al menos 20 caracteres.'
    hasError = true
  } else if (body.length > 1000) {
    newReviewBodyError.value = 'La descripción no puede superar los 1000 caracteres.'
    hasError = true
  }

  // Rating: obligatorio, entre 1 y 5
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    newReviewRatingError.value = 'El puntaje debe estar entre 1 y 5.'
    hasError = true
  }

  if (hasError) {
    createReviewError.value = 'Revisá los campos marcados en rojo.'
    return
  }

  creatingReview.value = true

  try {
    const payload = {
      title,
      body,
      rating,
    }

    await createSiteReview(siteId.value, payload)

    // Mostrar mensaje de éxito
    showSuccessMessage.value = true
    
    // Limpiar el formulario
    newReviewTitle.value = ''
    newReviewBody.value = ''
    newReviewRating.value = 5
    hoverReviewRating.value = 0

    // Ocultar mensaje de éxito después de 5 segundos
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 5000)

    // Recargar reseñas para mostrar la nueva
    await loadReviews()
    
    // Recargar datos del sitio para actualizar puntuación promedio
    await loadSite()
    
  } catch (error) {
    console.error('Error creando reseña:', error)
    const responseData = error?.response?.data

    // Manejar error específico de "ya tiene reseña"
    if (responseData?.error?.includes('Ya tienes una reseña')) {
      reviewSubmissionError.value = responseData.error
      userHasExistingReview.value = true
    } 
    // Manejar otros errores del backend
    else if (responseData?.error?.details) {
      const details = responseData.error.details
      
      if (details.title) {
        newReviewTitleError.value = details.title
      }
      if (details.body) {
        newReviewBodyError.value = details.body
      }
      if (details.rating) {
        newReviewRatingError.value = details.rating
      }

      createReviewError.value = 
        details.title || details.body || details.rating || 
        'No se pudo guardar la reseña.'
    } 
    // Error de validación general
    else if (responseData?.error) {
      reviewSubmissionError.value = responseData.error
    }
    // Error genérico
    else {
      reviewSubmissionError.value = 'No se pudo guardar la reseña. Por favor, intentá nuevamente.'
    }
  } finally {
    creatingReview.value = false
  }
}

// Carga inicial
onMounted(async () => {
  await loadSite()
  await loadImages()
  await loadFavoriteState()
  await loadReviews()
})

function goBackToList() {
  try {
    const raw = sessionStorage.getItem('site_list_state')
    if (raw) {
      const state = JSON.parse(raw)
      const query = state.query || {}
      // Si no venía page en query, usar el guardado
      if (!query.page && state.page) query.page = state.page
      router.push({ name: 'sites-list', query })
      return
    }
  } catch (e) {
    console.warn('No se pudo leer el estado del listado desde sessionStorage', e)
  }

  // Fallback: volver en el history
  router.back()
}
</script>

<!-- src/views/SiteDetailView.vue -->
<!-- Mantén todo el script como está, solo corrige el template: -->

<template>
  <div class="min-h-screen bg-linear-to-b from-slate-900 to-slate-800 text-white">
    <Topbar />

    <main class="max-w-5xl mx-auto pt-28 px-4 pb-12">
      <section v-if="loadingSite" class="text-center text-slate-300 py-12 text-sm">
        Cargando sitio...
      </section>

      <section v-else-if="siteError" class="text-center text-red-400 py-12 text-sm">
        {{ siteError }}
      </section>

      <section v-else-if="site" class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <!-- Columna principal con la info del sitio -->
        <article class="lg:col-span-2 bg-slate-900/70 rounded-xl border border-slate-700 p-6">
          <!-- Layout con imagen a la izquierda y contenido a la derecha -->
          <div class="flex flex-col md:flex-row gap-6">
            <div class="md:w-1/3">
              <img
                :src="site.image || ''"
                :alt="site.nombre"
                class="w-full h-64 md:h-full rounded-lg object-cover border border-slate-600"
              />
            </div>

            <div class="md:w-2/3 space-y-4">
              <!-- Título y ubicación -->
              <div>
                <h2 class="text-2xl md:text-3xl font-semibold text-sky-300">
                  {{ site.nombre }}
                </h2>
                <p class="mt-1 text-sm text-slate-300">{{ site.ciudad }} - {{ site.provincia }}</p>
                <div class="mt-1 flex items-center gap-3 text-sm text-slate-300">
                  <span>Puntuación:</span>
                  <div
                    class="rating-stars"
                    role="img"
                    :aria-label="ratingAriaLabel"
                    :title="ratingAriaLabel"
                  >
                    <svg
                      v-for="(fill, index) in ratingStars"
                      :key="`star-${index}`"
                      viewBox="0 0 24 24"
                      class="rating-star"
                    >
                      <defs>
                        <clipPath :id="`clip-star-${starUid}-${index}`">
                          <path :d="starPath" />
                        </clipPath>
                      </defs>
                      <rect
                        width="24"
                        height="24"
                        fill="rgba(148, 163, 184, 0.3)"
                        :clip-path="`url(#clip-star-${starUid}-${index})`"
                      />
                      <rect
                        :width="(fill / 100) * 24"
                        height="24"
                        fill="#facc15"
                        :clip-path="`url(#clip-star-${starUid}-${index})`"
                      />
                      <path
                        :d="starPath"
                        fill="none"
                        stroke="#facc15"
                        stroke-width="1.2"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </div>
                  <span class="text-xs text-slate-400">
                    <template v-if="ratingCount">
                      {{ averageRating.toFixed(1) }} / 5 · {{ ratingCount }} reseña{{
                        ratingCount === 1 ? '' : 's'
                      }}
                    </template>
                    <template v-else> Sin reseñas </template>
                  </span>
                </div>
              </div>

              <!-- Descripción breve -->
              <div>
                <p class="text-sm text-slate-500 mb-1">Descripción Breve:</p>
                <p class="text-sm text-slate-200">
                  {{ site.descripcionBreve }}
                </p>
              </div>

              <!-- Tags -->
              <div class="flex flex-wrap gap-2">
                <Tag
                  v-for="(tag, index) in site.tags"
                  :key="tag.id || index"
                  :tag="tag"
                  :selected-tags="[]"
                  :navigate="true"
                />
              </div>

              <!-- Información adicional -->
              <div class="space-y-2 text-sm">
                <p class="text-slate-400">
                  Estado de conservación:
                  <span class="font-semibold text-sky-300 ml-1">
                    {{ site.estado }}
                  </span>
                </p>

                <p v-if="site.añoInauguracion" class="text-slate-400">
                  Año de inauguración:
                  <span class="font-semibold text-slate-200 ml-1">
                    {{ site.añoInauguracion }}
                  </span>
                </p>

                <p v-if="site.lat && site.lng" class="text-slate-400">
                  Ubicación aproximada:
                  <span class="font-mono text-slate-200 ml-1">
                    {{ site.lat.toFixed(4) }}, {{ site.lng.toFixed(4) }}
                  </span>
                </p>
              </div>
            </div>
          </div>

          <!-- Accordion Descripción Completa -->
          <div
            class="mt-6 bg-slate-900/50 border border-slate-700 rounded-xl p-4 text-sm text-slate-200"
          >
            <button
              class="w-full text-left flex justify-between items-center font-semibold text-sky-300"
              @click="showFullDescription = !showFullDescription"
            >
              Descripción completa
              <span class="text-slate-400 text-xs">
                {{ showFullDescription ? '▲' : '▼' }}
              </span>
            </button>

            <transition name="fade">
              <p
                v-if="showFullDescription"
                class="mt-3 text-slate-300 leading-relaxed"
              >
                <!-- Si está vacío o es 'None', no mostrar nada -->
                {{ (site.descripcionCompleta && site.descripcionCompleta !== 'None')
                  ? site.descripcionCompleta
                  : '' }}
              </p>
            </transition>
          </div>
        </article>

        <!-- Columna lateral: favorito + reseña rápida -->
        <aside class="space-y-4">
          <section class="bg-slate-900/70 rounded-xl border border-slate-700 p-4">
            <h3 class="text-base font-semibold text-sky-300 mb-2">Marcá este sitio</h3>
            <button
              type="button"
              class="w-full py-2 rounded text-sm font-semibold flex items-center justify-center gap-2 border transition-colors"
              :class="
                isFavorite
                  ? 'bg-sky-500 text-slate-900 border-sky-400'
                  : 'bg-slate-800 text-slate-100 border-slate-600 hover:border-sky-400'
              "
              @click="handleToggleFavorite"
              :disabled="loadingFavorite"
            >
              <span v-if="loadingFavorite">Actualizando...</span>
              <span v-else>
                {{ isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos' }}
              </span>
            </button>
            <p v-if="!isAuthenticated" class="mt-2 text-[0.7rem] text-slate-400">
              Para marcar favoritos necesitás iniciar sesión.
            </p>
          </section>

          <!-- SECCIÓN DE RESEÑAS CORREGIDA -->
          <section class="bg-slate-900/70 rounded-xl border border-slate-700 p-4">
            <h3 class="text-base font-semibold text-sky-300 mb-2">Dejá tu reseña</h3>

            <!-- Mensaje de éxito -->
            <div 
              v-if="showSuccessMessage" 
              class="mb-3 p-3 bg-green-900/30 border border-green-600 rounded-lg"
            >
              <p class="text-sm text-green-300 flex items-center gap-2">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                ¡Reseña enviada exitosamente! Gracias por tu aporte.
              </p>
            </div>

            <!-- Mensaje de error específico (como "ya tiene reseña") -->
            <div 
              v-if="reviewSubmissionError && !createReviewError" 
              class="mb-3 p-3 bg-red-900/30 border border-red-600 rounded-lg"
            >
              <p class="text-sm text-red-300 flex items-center gap-2">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ reviewSubmissionError }}
              </p>
            </div>

            <p v-if="!isAuthenticated" class="text-xs text-slate-300">
              Iniciá sesión para poder escribir una reseña sobre este sitio.
            </p>

            <form v-else @submit.prevent="handleCreateReview" class="space-y-3">
              <div>
                <label class="block text-xs mb-1">Título</label>
                <input
                  v-model="newReviewTitle"
                  type="text"
                  class="w-full px-2 py-1.5 rounded bg-slate-800 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                  :class="newReviewTitleError ? 'border border-red-500' : 'border border-slate-600'"
                  placeholder="Una breve frase que resuma tu opinión"
                />
                <p v-if="newReviewTitleError" class="mt-1 text-[0.7rem] text-red-400">
                  {{ newReviewTitleError }}
                </p>
              </div>

              <div>
                <label class="block text-xs mb-1">Descripción</label>
                <textarea
                  v-model="newReviewBody"
                  rows="3"
                  class="w-full px-2 py-1.5 rounded bg-slate-800 text-xs resize-none focus:outline-none focus:ring-2 focus:ring-sky-500"
                  :class="newReviewBodyError ? 'border border-red-500' : 'border border-slate-600'"
                  placeholder="Contá brevemente tu experiencia con este sitio"
                ></textarea>
                <p v-if="newReviewBodyError" class="mt-1 text-[0.7rem] text-red-400">
                  {{ newReviewBodyError }}
                </p>
              </div>

              <div>
                <label class="flex items-center gap-2 text-xs mb-1">
                  Puntaje
                  <span class="text-[0.7rem] text-slate-400">{{ newReviewRating }} / 5</span>
                </label>
                <div
                  class="review-rating-picker"
                  role="radiogroup"
                  :aria-label="reviewRatingAria"
                  :class="newReviewRatingError ? 'ring-1 ring-red-500 rounded-md px-1' : ''"
                >
                  <button
                    v-for="star in interactiveReviewStars"
                    :key="star.value"
                    type="button"
                    class="review-rating-button"
                    :class="{ filled: star.filled }"
                    role="radio"
                    :aria-checked="newReviewRating === star.value"
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
                <p v-if="newReviewRatingError" class="mt-1 text-[0.7rem] text-red-400">
                  {{ newReviewRatingError }}
                </p>
              </div>

              <p v-if="createReviewError" class="text-xs text-red-400">
                {{ createReviewError }}
              </p>

              <button
                type="submit"
                :disabled="creatingReview"
                class="w-full py-2 rounded bg-sky-500 hover:bg-sky-400 text-slate-900 text-xs font-semibold transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {{ creatingReview ? 'Guardando...' : 'Enviar reseña' }}
              </button>
            </form>
          </section>

          <!-- Botón para volver a la lista con los querys-->
          <div class="mb-6">
            <button
              @click="goBackToList"
              class="inline-flex items-center gap-2 px-4 py-3 bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 hover:text-white rounded-xl transition-all duration-200 border border-slate-600 hover:border-sky-400 text-sm font-semibold group backdrop-blur-sm"
            >
              <svg
                class="w-4 h-4 transform group-hover:-translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Volver al listado
            </button>
          </div>
        </aside>
      </section>

      <!-- Mapa -->
      <section
        v-if="site && site.lat && site.lng"
        class="mt-6 bg-slate-900/70 rounded-xl border border-slate-700 p-6"
      >
        <h1 class="text-xl font-semibold text-sky-300 mb-4">Ubicación</h1>
        <SiteMap
          :key="`map-${site.lat}-${site.lng}`"
          :lat="site.lat"
          :lng="site.lng"
          :nombre="site.nombre"
          :descripcion-breve="site.descripcionBreve"
          :ciudad="site.ciudad"
        />
      </section>

      <!-- Carrusel de imágenes -->
      <section
        class="flex flex-col mt-8 gap-6 bg-slate-900/70 rounded-xl border border-slate-700 p-6"
      >
        <h1 class="text-2xl text-sky-300">Imágenes</h1>
        <SiteViewCarousel v-if="site" :images="siteImages" class="mt-8" />
      </section>

      <!-- Sección de reseñas de otros usuarios -->
      <section v-if="site" class="mt-8 bg-slate-900/70 rounded-xl border border-slate-700 p-6">
        <h3 class="text-lg font-semibold text-sky-300 mb-4">Reseñas de otros usuarios</h3>

        <p v-if="loadingReviews" class="text-sm text-slate-300">Cargando reseñas...</p>

        <p v-else-if="!hasReviews" class="text-sm text-slate-300">
          Todavía no hay reseñas para este sitio. Podés ser la primera persona en contar tu
          experiencia.
        </p>

        <div v-else class="space-y-4">
          <article
            v-for="review in reviews"
            :key="review.id"
            class="border border-slate-700 rounded-lg p-3 bg-slate-900/80"
          >
            <header class="flex justify-between items-center mb-1">
              <div>
                <div class="flex flex-row items-center gap-2 mb-1">
                  <div class="avatar">
                    <span>{{
                      review.user
                        ? review.user.name.charAt(0) + review.user.last_name.charAt(0)
                        : ''
                    }}</span>
                  </div>
                  <p class="text-sm text-slate-400">
                    {{ review.user ? review.user.name + ' ' + review.user.last_name : 'Anónimo' }}
                  </p>
                </div>
                <h4 class="text-sm font-semibold text-white">
                  {{ review.title }}
                </h4>
              </div>
              <div class="text-xs text-sky-300">⭐ {{ review.rating }}/5</div>
            </header>
            <p class="text-xs text-slate-200 whitespace-pre-line">
              {{ review.body }}
            </p>
            <p class="text-[0.7rem] text-slate-500 mt-2">
              Publicada el
              {{ new Date(review.created_at).toLocaleDateString('es-AR') }}
            </p>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.rating-stars {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.rating-star {
  width: 1.2rem;
  height: 1.2rem;
}

.rating-star rect {
  transition: width 200ms ease;
}

.avatar {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, #60a5fa, #1e40af);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f9fafb;
  font-weight: 600;
  font-size: 1.1rem;
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
