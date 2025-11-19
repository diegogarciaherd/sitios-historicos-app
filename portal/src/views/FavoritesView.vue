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
 *
 * Nota: la idea es mantener esta vista simple y declarativa.
 */

import { onMounted, ref } from 'vue'
import axios from 'axios'
import Topbar from '@/components/Topbar.vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

/**
 * Router para poder redirigir al login si no hay sesión.
 */
const router = useRouter()

/**
 * useAuth() expone:
 * - API_BASE_URL (la URL del backend Flask)
 * - token (JWT almacenado)
 * - isAuthenticated (bool reactivo)
 */
const { API_BASE_URL, token, isAuthenticated } = useAuth()

/**
 * Estados reactivos de UI.
 */
const loading = ref(true)          // Mientras carga favoritos
const errorMessage = ref('')       // Por si falla el request
const favorites = ref([])          // Lista de favoritos recibida del backend


/**
 * Función: carga los favoritos del usuario autenticado.
 *
 * Si NO hay sesión → redirijo a login.
 * Si hay sesión → llamo al endpoint GET /api/sites/users/me/favorites
 * y guardo la lista en "favorites".
 *
 * Manejo un try/catch para errores y dejo mensajes claros en pantalla.
 */
async function loadFavorites () {
  // Si el usuario no está autenticado → mando al login
  if (!isAuthenticated.value || !token.value) {
    router.push({ name: 'login' })
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''

    // Llamo a la API del backend
    const response = await axios.get(
      `${API_BASE_URL}/api/sites/users/me/favorites`,
      {
        headers: {
          Authorization: `Bearer ${token.value}` // Envío el JWT correctamente
        }
      }
    )

    // Guardo la lista que devuelve la API
    favorites.value = response.data ?? []
  } catch (error) {
    console.error('Error al cargar favoritos:', error)
    errorMessage.value = 'No se pudieron cargar tus favoritos.'
  } finally {
    loading.value = false
  }
}

// Cargo todo apenas se monta la vista
onMounted(loadFavorites)
</script>



<template>
  <!-- Fondo general del portal -->
  <div class="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
    <!-- Barra superior -->
    <Topbar />

    <!-- Contenido principal -->
    <main class="max-w-5xl mx-auto pt-28 px-4 pb-12">
      <h1 class="text-3xl font-bold mb-2">Mis sitios favoritos</h1>

      <p class="text-sm text-slate-300 mb-6">
        Acá vas a encontrar los sitios que marcaste como favoritos en el portal.
      </p>

      <!-- Contenedor principal -->
      <section class="bg-slate-900/70 rounded-xl shadow-lg p-6 border border-slate-700">
        
        <!-- Estado de carga -->
        <p v-if="loading" class="text-slate-200">
          Cargando favoritos...
        </p>

        <!-- Error del servidor -->
        <p v-else-if="errorMessage" class="text-sm text-red-400">
          {{ errorMessage }}
        </p>

        <!-- Si no tiene favoritos -->
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
              <h2 class="font-semibold">{{ fav.site_name }}</h2>
              
              <p class="text-xs text-slate-400">
                Marcado el:
                {{ new Date(fav.created_at).toLocaleString() }}
              </p>
            </div>

            <!-- Botón opcional futuro:
            <button class="text-red-300 text-sm hover:text-red-400">
              Quitar
            </button>
            -->
          </li>
        </ul>

      </section>
    </main>
  </div>
</template>
