<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { isAuthenticated, currentUser, logout } = useAuth()

// Estado para controlar el menú mobile
const mobileMenuOpen = ref(false)

const userName = computed(() => currentUser.value?.name || currentUser.value?.email || 'Cuenta')

const goToLogin = () => {
  if (route.name === 'login') return
  router.push({ name: 'login' })
  mobileMenuOpen.value = false
}

const goToProfile = () => {
  if (route.name === 'profile') return
  router.push({ name: 'profile' })
  mobileMenuOpen.value = false
}

const goToFavorites = () => {
  if (route.name === 'favorites') return
  router.push({ name: 'favorites' })
  mobileMenuOpen.value = false
}

const handleLogout = () => {
  logout()
  router.push({ name: 'home' })
  mobileMenuOpen.value = false
}
</script>

<template>
  <header
    class="w-full bg-slate-900/95 text-slate-50 border-b border-slate-800 sticky top-0 z-2000"
  >
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

        <!-- Si está autenticada -->
        <div v-else class="flex items-center gap-2">
          <!-- Desktop: botones visibles -->
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

          <!-- Desktop: info usuario -->
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

          <!-- Mobile: Avatar con menú desplegable -->
          <div class="sm:hidden relative">
            <button
              type="button"
              class="flex items-center gap-1 p-1 rounded-full hover:bg-slate-800 transition"
              @click="mobileMenuOpen = !mobileMenuOpen"
            >
              <!-- Avatar pequeño -->
              <div class="w-7 h-7 rounded-full bg-sky-500 flex items-center justify-center text-xs font-bold">
                {{ userName.charAt(0).toUpperCase() }}
              </div>
              <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Menú desplegable mobile -->
            <transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <div
                v-if="mobileMenuOpen"
                class="absolute right-0 top-full mt-1 w-48 py-2 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50"
                @click.stop
              >
                <!-- Info usuario -->
                <div class="px-4 py-2 border-b border-slate-700">
                  <p class="text-xs font-semibold truncate">{{ userName }}</p>
                  <p class="text-[11px] text-slate-400 truncate">{{ currentUser?.email }}</p>
                </div>
                
                <!-- Opciones -->
                <button
                  type="button"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-slate-700 transition flex items-center gap-2"
                  @click="goToProfile"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  Mi perfil
                </button>
                
                <button
                  type="button"
                  class="w-full text-left px-4 py-2 text-sm hover:bg-slate-700 transition flex items-center gap-2"
                  @click="goToFavorites"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                  </svg>
                  Mis favoritos
                </button>
                
                <!-- Separador -->
                <div class="border-t border-slate-700 my-1"></div>
                
                <button
                  type="button"
                  class="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-slate-700 transition flex items-center gap-2"
                  @click="handleLogout"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  Cerrar sesión
                </button>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* Cerrar menú al hacer clic fuera */
@media (max-width: 640px) {
  .mobile-menu-open {
    position: fixed;
    inset: 0;
    z-index: 40;
  }
}
</style>