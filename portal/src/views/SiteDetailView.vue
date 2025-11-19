<!-- src/views/SiteDetailView.vue -->
<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Topbar from '@/components/Topbar.vue'
import { getSiteById, getSiteCoverImage, getSiteImages } from '@/api/sites'
import { getSiteReviews, createSiteReview } from '@/api/reviews'
import { toggleFavoriteRequest, getMyFavoritesRequest } from '@/api/favorites'
import { useAuth } from '@/composables/useAuth'
import SiteViewCarousel from '@/components/SiteViewCarousel.vue'
import SiteMap from '@/components/SiteMap.vue'
import { useSiteSearch } from '@/composables/useSiteSearch'

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()
const { goBackToList } = useSiteSearch()
const site = ref(null)
const loadingSite = ref(false)
const errorSite = ref('')

const reviews = ref([])
const loadingReviews = ref(false)

const isFavorite = ref(false)
const loadingFavorite = ref(false)

const newReviewTitle = ref('')
const newReviewBody = ref('')
const newReviewRating = ref(5)
const creatingReview = ref(false)
const createReviewError = ref('')

const siteId = computed(() => Number(route.params.id))
const siteImages = ref([])

const showFullDescription = ref(false)

async function loadSite() {
  loadingSite.value = true
  errorSite.value = ''

  try {
    const data = await getSiteById(siteId.value)
    site.value = data
    site.value.image = await getSiteCoverImage(siteId.value)
  } catch (error) {
    console.error('Error cargando sitio:', error)
    errorSite.value = 'No se pudo cargar el sitio.'
  } finally {
    loadingSite.value = false
  }
}

async function loadReviews() {
  loadingReviews.value = true

  try {
    const data = await getSiteReviews(siteId.value)
    // Si el backend devuelve [reviews, meta], usar data[0]; si es array directo, usar data
    reviews.value = Array.isArray(data) ? data : Array.isArray(data[0]) ? data[0] : []
  } catch (error) {
    console.error('Error cargando reseñas:', error)
  } finally {
    loadingReviews.value = false
  }
}

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

async function loadImages() {
  try {
    const images = await getSiteImages(siteId.value)
    siteImages.value = images
  } catch (error) {
    console.error('Error cargando imágenes del sitio:', error)
  }
}

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
      // fallback si el backend no devuelve el flag
      isFavorite.value = !isFavorite.value
    }
  } catch (error) {
    console.error('Error alternando favorito:', error)
  } finally {
    loadingFavorite.value = false
  }
}

async function handleCreateReview() {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }

  createReviewError.value = ''
  creatingReview.value = true

  try {
    const payload = {
      title: newReviewTitle.value,
      body: newReviewBody.value,
      rating: newReviewRating.value,
    }

    await createSiteReview(siteId.value, payload)

    // Limpiamos el formulario y recargamos reseñas
    newReviewTitle.value = ''
    newReviewBody.value = ''
    newReviewRating.value = 5
    await loadReviews()
  } catch (error) {
    console.error('Error creando reseña:', error)
    createReviewError.value = 'No se pudo guardar la reseña.'
  } finally {
    creatingReview.value = false
  }
}

const hasReviews = computed(() => reviews.value.length > 0)

onMounted(async () => {
  await loadSite()
  if (site.value) {
    await Promise.all([loadReviews(), loadFavoriteState(), loadImages()])
  }
})
</script>

<template>
  <div class="min-h-screen bg-linear-to-b from-slate-900 to-slate-800 text-white">
    <Topbar />

    <main class="max-w-5xl mx-auto pt-28 px-4 pb-12">
      <section v-if="loadingSite" class="text-center text-slate-300 py-12 text-sm">
        Cargando sitio...
      </section>

      <section v-else-if="errorSite" class="text-center text-red-400 py-12 text-sm">
        {{ errorSite }}
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
                <span
                  v-for="(tag, index) in site.tags"
                  :key="index"
                  class="px-2 py-1 rounded-full bg-slate-700 text-xs text-slate-100"
                >
                  {{ tag.name }}
                </span>
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
              <p v-if="showFullDescription" class="mt-3 text-slate-300 leading-relaxed">
                {{ site.descripcionCompleta }}
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

          <section class="bg-slate-900/70 rounded-xl border border-slate-700 p-4">
            <h3 class="text-base font-semibold text-sky-300 mb-2">Dejá tu reseña</h3>

            <p v-if="!isAuthenticated" class="text-xs text-slate-300">
              Iniciá sesión para poder escribir una reseña sobre este sitio.
            </p>

            <form v-else @submit.prevent="handleCreateReview" class="space-y-3">
              <div>
                <label class="block text-xs mb-1">Título</label>
                <input
                  v-model="newReviewTitle"
                  type="text"
                  required
                  class="w-full px-2 py-1.5 rounded bg-slate-800 border border-slate-600 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                  placeholder="Una breve frase que resuma tu opinión"
                />
              </div>

              <div>
                <label class="block text-xs mb-1">Descripción</label>
                <textarea
                  v-model="newReviewBody"
                  rows="3"
                  required
                  class="w-full px-2 py-1.5 rounded bg-slate-800 border border-slate-600 text-xs resize-none focus:outline-none focus:ring-2 focus:ring-sky-500"
                  placeholder="Contá brevemente tu experiencia con este sitio"
                ></textarea>
              </div>

              <div>
                <label class="block text-xs mb-1">Puntaje</label>
                <select
                  v-model.number="newReviewRating"
                  class="w-full px-2 py-1.5 rounded bg-slate-800 border border-slate-600 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
                >
                  <option v-for="n in 5" :key="n" :value="n">
                    {{ n }} estrella{{ n > 1 ? 's' : '' }}
                  </option>
                </select>
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
          <!-- Bton para volver a la lista con los querys-->
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

      <!-- Sección de reseñas -->
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
              <h4 class="text-sm font-semibold text-white">
                {{ review.title }}
              </h4>
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

<style></style>
