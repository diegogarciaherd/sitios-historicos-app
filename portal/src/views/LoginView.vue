<!-- src/views/LoginView.vue -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Topbar from '@/components/Topbar.vue'
import { useAuth } from '@/composables/useAuth'
import { onMounted } from "vue";
import { handleCredentialResponse } from '@/api/auth';

const router = useRouter()
const { isAuthenticated, login } = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleSubmit () {
  errorMessage.value = ''
  loading.value = true

  const result = await login(email.value, password.value)

  loading.value = false

  if (!result.ok) {
    errorMessage.value = result.message || 'No se pudo iniciar sesión.'
    return
  }

  router.push({ name: 'home' })
}

onMounted(() => {
  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: () => (handleCredentialResponse, router.push("/"))
  });

  window.google.accounts.id.renderButton(
    document.getElementById("googleBtn"),
    { theme: "outline", size: "large" }
  );
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
    <Topbar />

    <main class="max-w-md mx-auto pt-28 px-4 pb-12">
      <section class="bg-slate-900/70 rounded-xl shadow-lg p-6 border border-slate-700">
        <h2 class="text-2xl font-semibold mb-4 text-sky-300">Iniciar sesión</h2>
        <p class="text-sm text-slate-300 mb-6">
          Accedé para marcar sitios como favoritos y dejar reseñas.
        </p>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm mb-1">Email</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-3 py-2 rounded bg-slate-800 border border-slate-600 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="tucorreo@ejemplo.com"
            />
          </div>

          <div>
            <label class="block text-sm mb-1">Contraseña</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-3 py-2 rounded bg-slate-800 border border-slate-600 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="••••••••"
            />
          </div>

          <p v-if="errorMessage" class="text-sm text-red-400">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 py-2 rounded bg-sky-500 hover:bg-sky-400 text-slate-900 font-semibold transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Ingresando...' : 'Ingresar' }}
          </button>
        </form>
      </section>

      <p class="mt-4 text-xs text-slate-400">
        Si contas con una cuenta de Google:
      </p>
      <div id="googleBtn" style="margin-top: 5px"></div>
    </main>
  </div>
</template>
