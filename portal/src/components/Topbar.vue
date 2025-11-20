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
    class="w-full flex items-center justify-between px-8 py-4 fixed top-0 left-0 right-0 z-50 bg-gradient-to-b from-slate-900 via-slate-900/80 to-transparent"
  >
    <!-- Logo + título, siempre lleva a la home -->
    <RouterLink class="flex flex-row items-center gap-3" to="/">
      <img src="@/assets/logo.png" alt="Logo" class="w-8" />
      <h1 class="text-[1.5rem] text-white hover:text-sky-300 transition-colors duration-300">
        Registro de sitios históricos
      </h1>
    </RouterLink>

    <!-- Buscador + navegación principal -->
    <nav class="flex items-center gap-6">
      <!-- Link a listado de sitios -->
      <RouterLink
        to="/sitios"
        class="rounded-lg bg-sky-900 px-4 py-2 text-white text-sm md:text-base hover:scale-105 transition-transform duration-300"
      >
        Sitios históricos
      </RouterLink>

      <!-- Acerca de -->
      <RouterLink
        to="/about"
        class="text-white text-sm md:text-base hover:text-sky-300 transition-colors duration-300"
      >
        Acerca de
      </RouterLink>

      <!-- Contacto -->
      <RouterLink
        to="/contact"
        class="text-white text-sm md:text-base hover:text-sky-300 transition-colors duration-300"
      >
        Contacto
      </RouterLink>

      <!-- Si NO estoy logueada, muestro solo "Iniciar sesión" -->
      <RouterLink
        v-if="!isAuthenticated"
        to="/login"
        class="text-white text-sm md:text-base hover:text-sky-300 transition-colors duration-300"
      >
        Iniciar sesión
      </RouterLink>

      <!-- Si estoy logueada, muestro Mis favoritos + Cerrar sesión -->
      <div
        v-else
        class="flex items-center gap-4"
      >
        <!-- Link a la vista de favoritos -->
        <RouterLink
          :to="{ name: 'favorites' }"
          class="text-white text-sm md:text-base hover:text-sky-300 transition-colors duration-300"
        >
          Mis favoritos
        </RouterLink>

        <!-- Nombre / mail de referencia -->
        <span class="text-xs md:text-sm text-slate-300 hidden sm:inline">
          {{ currentUserEmail || 'Mi perfil' }}
        </span>

        <!-- Botón logout -->
        <button
          type="button"
          class="text-white text-sm md:text-base hover:text-red-400 transition-colors duration-300"
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
