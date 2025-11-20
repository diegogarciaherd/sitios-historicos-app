<!-- src/components/Topbar.vue -->
<script setup>
/**
 * Topbar del portal público.
 *
 * Acá muestro:
 * - Logo + link a la home.
 * - Buscador simple con selector de criterio (nombre/provincia/ciudad).
 * - Link a "Sitios históricos".
 * - Links estáticos a "Acerca de" y "Contacto".
 * - Y según si estoy logueada o no:
 *   - "Iniciar sesión" (si NO hay token)
 *   - Un menú de cuenta con accesos a favoritos y logout (si SÍ hay token)
 */

import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isAuthenticated, currentUserEmail, logout } = useAuth()

const accountMenuOpen = ref(false)
const accountMenuRef = ref(null)

const searchbarOption = ref('name')
const searchQuery = ref('')

function toggleAccountMenu() {
  accountMenuOpen.value = !accountMenuOpen.value
}

function closeAccountMenu() {
  accountMenuOpen.value = false
}

function handleDocumentClick(event) {
  if (!accountMenuRef.value) return
  if (accountMenuRef.value.contains(event.target)) return
  accountMenuOpen.value = false
}

/**
 * Cierro sesión y vuelvo a la página principal del portal.
 */
async function handleLogout() {
  closeAccountMenu()
  logout()
  try {
    await router.push({ name: 'home' })
  } catch (e) {
    // Si ya estoy en home, no pasa nada
    console.error(e)
  }
}

function handleSearch() {
  const query = searchQuery.value.trim()
  if (query === '') return

  router.push(`/sitios?${searchbarOption.value}=${encodeURIComponent(query)}`)
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <div
    class="w-full justify-between items-center px-8 py-4 flex fixed top-0 bg-transparent z-1000 bg-linear-to-b from-gray-400 via-30% to-transparent"
  >
    <!-- Logo + título, siempre lleva a la home -->
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1 class="text-[1.5rem] text-white hover:text-sky-300 transition-colors duration-300">
        Registro de sitios históricos
      </h1>
    </RouterLink>

    <!-- Buscador + selector (branch de tus compas) -->
    <div class="relative right-2 w-[40%] hidden md:block">
      <input
        type="text"
        class="flex w-full rounded-full bg-transparent border border-white/50 focus:border-white focus:bg-white/20 focus:outline-none transition-colors duration-300 text-white px-4 py-1 pr-28"
        placeholder="Buscar..."
        v-model="searchQuery"
        v-on:keyup.enter="handleSearch"
      />
      <select
        class="absolute top-1/2 right-0 -translate-y-1/2 text-gray-600 bg-white outline-none border-none appearance-none pr-6 pl-3 py-1 rounded-r-full text-sm"
        v-model="searchbarOption"
      >
        <option value="name" selected>Nombre</option>
        <option value="province">Provincia</option>
        <option value="city">Ciudad</option>
      </select>
    </div>

    <!-- Navegación principal -->
    <nav class="flex items-center">
      <!-- Botón a la vista de sitios históricos (branch compas) -->
      <RouterLink
        to="/sitios"
        class="rounded-lg bg-sky-900 px-6 py-3 text-white text-lg hover:scale-105 transition-transform duration-300"
      >
        Sitios históricos
      </RouterLink>

      <!-- Si NO estoy logueada, muestro solo "Iniciar sesión" -->
      <RouterLink
        v-if="!isAuthenticated"
        to="/login"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
      >
        Iniciar sesión
      </RouterLink>

      <!-- Si estoy logueada, muestro Mis favoritos + Cerrar sesión -->
      <div v-else class="ml-6 relative" ref="accountMenuRef">
        <button
          type="button"
          class="flex items-center gap-2 rounded-lg bg-slate-800/80 px-4 py-2 text-white text-sm md:text-base border border-slate-600 hover:border-sky-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 transition-colors duration-300"
          @click.stop="toggleAccountMenu"
          @keydown.escape.prevent="closeAccountMenu"
          aria-haspopup="true"
          :aria-expanded="accountMenuOpen"
        >
          Cuenta
        </button>

        <div
          v-if="accountMenuOpen"
          class="absolute right-0 mt-2 w-52 rounded-xl border border-slate-700 bg-slate-900/95 shadow-lg py-2 z-50"
          role="menu"
        >
          <p
            class="px-4 pb-2 text-xs text-slate-400 border-b border-slate-700"
            v-if="currentUserEmail"
          >
            Sesión iniciada como
            <span class="block font-semibold text-slate-200">{{ currentUserEmail }}</span>
          </p>
          <RouterLink
            to="/favorites"
            class="block px-4 py-2 text-sm text-slate-100 hover:bg-slate-800 transition-colors duration-200"
            role="menuitem"
            @click="closeAccountMenu"
          >
            Mis favoritos
          </RouterLink>
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-red-300 hover:bg-slate-800 transition-colors duration-200 cursor-pointer"
            role="menuitem"
            @click="handleLogout"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </nav>
  </div>
</template>

<style scoped>
/* Por ahora no necesito estilos extra, todo va con Tailwind. */
</style>
