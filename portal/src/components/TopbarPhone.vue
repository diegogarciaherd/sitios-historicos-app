<!-- src/components/Topbar.vue -->
<script setup>
/**
 * Topbar del portal público.
 *
 * - Logo + link a la home.
 * - Link a "Sitios históricos".
 * - Links estáticos a "Acerca de" y "Contacto".
 * - Según autenticación:
 *   - Si NO hay token → botón "Iniciar sesión".
 *   - Si SÍ hay token → botones "Mi perfil", "Mis favoritos" y "Cerrar sesión".
 */

import { computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()

const { isAuthenticated, currentUser, logout } = useAuth()

const userName = computed(() => currentUser.value?.name || currentUser.value?.email || 'Cuenta')

const goToLogin = () => {
  if (route.name === 'login') return
  router.push({ name: 'login' })
}

const goToProfile = () => {
  if (route.name === 'profile') return
  router.push({ name: 'profile' })
}

const goToFavorites = () => {
  if (route.name === 'favorites') return
  router.push({ name: 'favorites' })
}

const handleLogout = () => {
  logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <!-- 👇 acá el cambio importante: sticky + z-50 -->
  <header class="w-full bg-slate-900/95 text-slate-50 border-b border-slate-800 sticky top-0 z-50">
    <div class="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-4">
      <!-- Logo + título -->
      <RouterLink to="/" class="flex items-center gap-2 hover:opacity-90 transition">
        <div
          class="w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center text-xs font-bold"
        >
          RS
        </div>
        <span class="font-semibold tracking-tight text-sm sm:text-base">
          Registro de sitios históricos
        </span>
      </RouterLink>

      <!-- Navegación principal -->
      <nav class="hidden md:flex items-center gap-4 text-sm">
        <RouterLink
          to="/sitios"
          class="hover:text-sky-300 transition"
          :class="{
            'text-sky-300': route.name === 'sites-list' || route.name === 'site-detail',
          }"
        >
          Sitios históricos
        </RouterLink>
      </nav>

      <!-- Área de cuenta -->
      <div class="flex items-center gap-2">
        <!-- Si NO está autenticada: botón de login -->
        <button
          v-if="!isAuthenticated"
          type="button"
          class="px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium bg-sky-500 hover:bg-sky-600 transition shadow-sm"
          @click="goToLogin"
        >
          Iniciar sesión
        </button>

        <!-- Si está autenticada: perfil + favoritos + logout -->
        <div v-else class="flex items-center gap-2">
          <button
            type="button"
            class="hidden sm:inline-flex px-3 py-1.5 rounded-full text-xs sm:text-sm bg-slate-800 hover:bg-slate-700 transition"
            @click="goToProfile"
          >
            Mi perfil
          </button>

          <button
            type="button"
            class="hidden sm:inline-flex px-3 py-1.5 rounded-full text-xs sm:text-sm bg-slate-800 hover:bg-slate-700 transition"
            @click="goToFavorites"
          >
            Mis favoritos
          </button>

          <!-- Avatar / nombre -->
          <div class="hidden sm:flex flex-col items-end">
            <span class="text-xs font-semibold leading-tight">
              {{ userName }}
            </span>
            <button
              type="button"
              class="text-[11px] text-slate-400 hover:text-sky-300 transition"
              @click="handleLogout"
            >
              Cerrar sesión
            </button>
          </div>

          <!-- En mobile solo mostramos un botón simple de logout -->
          <button
            type="button"
            class="sm:hidden px-2 py-1 rounded-full text-xs bg-slate-800 hover:bg-slate-700 transition"
            @click="handleLogout"
          >
            Salir
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* Todo el estilo está con Tailwind en el template. */
</style>
