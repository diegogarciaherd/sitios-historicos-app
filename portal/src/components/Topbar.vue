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
 *   - "Mis favoritos" + "Cerrar sesión" (si SÍ hay token)
 */

import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isAuthenticated, currentUserEmail, logout } = useAuth()

/**
 * Cierro sesión y vuelvo a la página principal del portal.
 */
async function handleLogout () {
  logout()
  try {
    await router.push({ name: 'home' })
  } catch (e) {
    // Si ya estoy en home, no pasa nada
    console.error(e)
  }
}
</script>

<template>
  <div
    class="w-full flex items-center justify-between px-8 py-4 fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-slate-900 via-slate-900/80 to-transparent overflow-hidden"
  >
    <!-- Logo + título, siempre lleva a la home -->
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1
        class="text-[1.5rem] text-white hover:text-sky-300 transition-colors duration-300"
      >
        Registro de sitios históricos
      </h1>
    </RouterLink>

    <!-- Buscador + selector (branch de tus compas) -->
    <div class="relative right-2 w-[40%] hidden md:block">
      <input
        type="text"
        class="flex w-full rounded-full bg-transparent border border-white/50 focus:border-white focus:bg-white/20 focus:outline-none transition-colors duration-300 text-white px-4 py-1 pr-28"
        placeholder="Buscar..."
      />
      <select
        class="absolute top-1/2 right-0 -translate-y-1/2 text-gray-600 bg-white outline-none border-none appearance-none pr-6 pl-3 py-1 rounded-r-full text-sm"
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

      <!-- Links estáticos -->
      <RouterLink
        to="/about"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
      >
        Acerca de
      </RouterLink>

      <RouterLink
        to="/contact"
        class="ml-6 text-white text-lg hover:text-sky-300 transition-colors duration-300"
      >
        Contacto
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
      <div
        v-else
        class="ml-6 flex items-center gap-4"
      >
        <!-- Link a la vista de favoritos -->
        <RouterLink
          to="/favorites"
          class="text-white text-lg hover:text-sky-300 transition-colors duration-300"
        >
          Mis favoritos
        </RouterLink>

        <!-- Nombre / mail de referencia + botón de logout -->
        <span class="text-sm text-slate-300 hidden md:inline">
          {{ currentUserEmail || 'Mi perfil' }}
        </span>

        <button
          type="button"
          class="text-white text-lg hover:text-red-400 transition-colors duration-300"
          @click="handleLogout"
        >
          Cerrar sesión
        </button>
      </div>
    </nav>
  </div>
</template>

<style scoped>
/* Por ahora no necesito estilos extra, todo va con Tailwind. */
</style>
