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

          <button class="back-button" type="button" @click="goBack">
            ← Volver
          </button>
        </header>

        <!-- Pestañas -->
        <nav class="tabs">
          <button
            :class="{ active: activeTab === 'reviews' }"
            @click="activeTab = 'reviews'"
          >
            Mis reseñas
          </button>
          <button
            :class="{ active: activeTab === 'favorites' }"
            @click="activeTab = 'favorites'"
          >
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
            <li v-for="review in reviews" :key="review.id" class="item-card">
              <h3 class="item-title">{{ review.site_name }}</h3>
              <p class="meta">
                {{ formatDate(review.created_at) }} · ★ {{ review.rating }}
              </p>
              <p class="excerpt">
                {{ review.excerpt }}
              </p>
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
              :disabled="
                reviewsMeta.page * reviewsMeta.per_page >= reviewsMeta.total
              "
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

          <div
            v-if="favoritesMeta.total > favoritesMeta.per_page"
            class="pager"
          >
            <button
              :disabled="favoritesMeta.page === 1"
              @click="changeFavoritesPage(favoritesMeta.page - 1)"
            >
              Anterior
            </button>
            <span>Página {{ favoritesMeta.page }}</span>
            <button
              :disabled="
                favoritesMeta.page * favoritesMeta.per_page >=
                favoritesMeta.total
              "
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Topbar from '@/components/Topbar.vue'
import { useAuth } from '@/composables/useAuth'
import { fetchMyReviews, fetchMyFavorites } from '@/api/profile'

const router = useRouter()
const { currentUser, isAuthenticated } = useAuth()

const user = computed(() => currentUser.value)

const activeTab = ref('reviews')

// RESEÑAS
const reviews = ref([])
const reviewsMeta = ref({ page: 1, per_page: 25, total: 0 })
const reviewsOrder = ref('desc')
const loadingReviews = ref(false)

// FAVORITOS
const favorites = ref([])
const favoritesMeta = ref({ page: 1, per_page: 25, total: 0 })
const favoritesOrder = ref('desc')
const loadingFavorites = ref(false)

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
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }

  await loadReviews()
  await loadFavorites()
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
  favoritesOrder.value === 'desc'
    ? 'Más nuevos primero'
    : 'Más antiguos primero',
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
  display: flex;
  border-radius: 999px;
  background: #e5e7eb;
  padding: 0.25rem;
  margin-bottom: 1.25rem;
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
}

.tabs button.active {
  background: #2563eb;
  color: #ffffff;
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

.excerpt {
  font-size: 0.9rem;
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
