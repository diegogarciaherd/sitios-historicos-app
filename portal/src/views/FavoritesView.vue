<!-- src/views/FavoritesView.vue -->
<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import Topbar from '@/components/Topbar.vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const router = useRouter()
const { API_BASE_URL, token, isAuthenticated } = useAuth()

const loading = ref(true)
const errorMessage = ref('')
const favorites = ref([])

async function loadFavorites () {
  if (!isAuthenticated.value || !token.value) {
    // Si no hay sesión, mandamos al login
    router.push({ name: 'login' })
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''

    const response = await axios.get(
      `${API_BASE_URL}/api/sites/users/me/favorites`
    )

    favorites.value = response.data ?? []
  } catch (error) {
    console.error('Error al cargar favoritos:', error)
    errorMessage.value = 'No se pudieron cargar tus favoritos.'
  } finally {
    loading.value = false
  }
}

onMounted(loadFavorites)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
    <Topbar />

    <main class="max-w-5xl mx-auto pt-28 px-4 pb-12">
      <h1 class="text-3xl font-bold mb-2">Mis sitios favoritos</h1>
      <p class="text-sm text-slate-300 mb-6">
        Acá vas a encontrar los sitios que marcaste como favoritos en el portal.
      </p>

      <section class="bg-slate-900/70 rounded-xl shadow-lg p-6 border border-slate-700">
        <p v-if="loading" class="text-slate-200">
          Cargando favoritos...
        </p>

        <p v-else-if="errorMessage" class="text-sm text-red-400">
          {{ errorMessage }}
        </p>

        <p v-else-if="favorites.length === 0" class="text-slate-300">
          Todavía no marcaste ningún sitio como favorito.
        </p>

        <ul v-else class="space-y-3">
          <li
            v-for="fav in favorites"
            :key="fav.site_id"
            class="bg-slate-800 rounded-lg px-4 py-3 flex justify-between items-center border border-slate-700"
          >
            <div>
              <h2 class="font-semibold">
                {{ fav.site_name }}
              </h2>
              <p class="text-xs text-slate-400">
                Marcado el: {{ new Date(fav.created_at).toLocaleString() }}
              </p>
            </div>

            <!-- Más adelante podríamos linkear al detalle del sitio -->
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>
