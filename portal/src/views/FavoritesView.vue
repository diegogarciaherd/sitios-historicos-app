<!-- src/views/FavoritesView.vue -->
<script setup>
/**
 * Vista: Mis sitios favoritos
 * -------------------------------------
 * Acá muestro todos los sitios que el usuario marcó como favoritos
 * en el portal público. Es parte del perfil del usuario.
 *
 * La lógica es simple:
 * - Si el usuario no está logueado → lo mando al login.
 * - Si está logueado → pido al backend todos los favoritos.
 * - Manejo estado de carga, errores y listado vacío.
 */

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Topbar from '@/components/TopbarPhone.vue'
import { useAuth } from '@/composables/useAuth'
import { getMyFavoritesRequest } from '@/api/favorites'

const router = useRouter()
const { isAuthenticated, token } = useAuth()

const loading = ref(true)
const errorMessage = ref('')
const favorites = ref([])

/**
 * Carga la lista de favoritos del usuario logueado.
 */
async function loadFavorites() {
  // Si no hay sesión, mando al login
  if (!isAuthenticated.value || !token.value) {
    router.push({ name: 'login' })
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''

    const data = await getMyFavoritesRequest()
    favorites.value = Array.isArray(data) ? data : []
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
        <!-- Estado de carga -->
        <p v-if="loading" class="text-slate-200">Cargando favoritos...</p>

        <!-- Error al cargar -->
        <p v-else-if="errorMessage" class="text-sm text-red-400">
          {{ errorMessage }}
        </p>

        <!-- Lista vacía -->
        <p v-else-if="favorites.length === 0" class="text-slate-300">
          Todavía no marcaste ningún sitio como favorito.
        </p>

        <!-- Lista de favoritos -->
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
                Marcado el:
                {{ new Date(fav.created_at).toLocaleString() }}
              </p>
            </div>

            <!-- Futuro: podríamos agregar un botón para ir al detalle del sitio -->
            <!--
            <RouterLink
              :to="{ name: 'site-detail', params: { id: fav.site_id } }"
              class="text-sky-300 text-xs hover:underline"
            >
              Ver detalle
            </RouterLink>
            -->
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>
