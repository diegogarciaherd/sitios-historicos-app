// src/composables/useAuth.js
/**
 * Manejo de autenticación en el portal público.
 *
 * - Hace login contra la API de Flask: POST /api/auth/
 * - Guarda el JWT en localStorage.
 * - Expone estado reactivo para saber si hay usuario logueado.
 *
 * La idea es que desde cualquier componente pueda preguntar:
 *   - isAuthenticated → boolean
 *   - currentUser / currentUserEmail → datos básicos
 *   - login(email, password)
 *   - logout()
 */

import { ref, computed, watchEffect } from 'vue'
import axios from 'axios'
import api from '../api/base'

// URL base de la API (sin /api al final, lo agrego a mano donde haga falta)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Estado global simple en memoria (para todo el portal)
const token = ref(localStorage.getItem('jwt') || null)
const currentUserEmail = ref(localStorage.getItem('currentUserEmail') || null)
const currentUser = ref(null)

const isAuthenticated = computed(() => !!token.value)

/**
 * Setea o limpia el header Authorization de axios a partir del token actual.
 * No afecta a la instancia `api` que vive en src/api/base.js, pero me sirve
 * si en algún momento uso axios "global".
 */
function setAxiosAuthHeader(jwt) {
  if (jwt) {
    axios.defaults.headers.common.Authorization = `Bearer ${jwt}`
  } else {
    delete axios.defaults.headers.common.Authorization
  }
}

// Inicializo axios con el token que haya en localStorage
setAxiosAuthHeader(token.value)

// Cada vez que cambie el token, actualizo el header de axios global
watchEffect(() => {
  setAxiosAuthHeader(token.value)
})

/**
 * Hace login contra la API pública.
 *
 * Llama a:
 *   POST {API_BASE_URL}/api/auth/
 * body:
 *   { email, password }
 */
async function login(email, password) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/`, {
      email,
      password,
    })

    const data = response.data || {}
    const jwt = data.access_token || data.token

    if (!jwt) {
      // El backend debería devolver siempre access_token/token cuando el login es correcto
      return {
        ok: false,
        message: 'El servidor no devolvió un token válido.',
      }
    }

    // Guardo token en memoria + localStorage
    token.value = jwt
    localStorage.setItem('jwt', jwt)

    // Guardo info básica de usuario (email + lo que venga en data.user)
    const userFromBackend = data.user || {}
    currentUser.value = {
      id: data.user_id ?? userFromBackend.id ?? null,
      email: userFromBackend.email ?? email,
      name: userFromBackend.name ?? '',
      last_name: userFromBackend.last_name ?? '',
    }

    currentUserEmail.value = currentUser.value.email
    localStorage.setItem('currentUserEmail', currentUserEmail.value)

    return { ok: true }
  } catch (error) {
    console.error('Error en login:', error)

    let message = 'No se pudo iniciar sesión.'

    if (error.response?.status === 401) {
      message = 'Credenciales inválidas.'
    } else if (error.response?.data?.error?.message) {
      // El backend a veces devuelve un array de mensajes, a veces un string
      const raw = error.response.data.error.message
      message = Array.isArray(raw) ? raw.join(' ') : raw
    }

    return {
      ok: false,
      message,
    }
  }
}

export async function handleCredentialResponse(response) {
  try {
    const algo = response.credential
    const res = await api.post('/auth/google', { token: algo })
    const data = res.data || {}
    const jwt = data.access_token
    token.value = jwt
    localStorage.setItem('jwt', jwt)

    const userFromBackend = data.user || {}
    currentUser.value = {
      id: data.user_id ?? userFromBackend.id ?? null,
      email: userFromBackend.email ?? email,
      name: userFromBackend.name ?? '',
    }

    currentUserEmail.value = currentUser.value.email
    localStorage.setItem('currentUserEmail', currentUserEmail.value)

    return { ok: true }
  } catch (error) {
    console.error('Error en login:', error)

    let message = 'No se pudo iniciar sesión.'

    if (error.response?.status === 401) {
      message = 'Credenciales inválidas.'
    } else if (error.response?.data?.error?.message) {
      // El backend a veces devuelve un array de mensajes, a veces un string
      const raw = error.response.data.error.message
      message = Array.isArray(raw) ? raw.join(' ') : raw
    }

    return {
      ok: false,
      message,
    }
  }
}

/**
 * Cierra la sesión del usuario:
 * - Limpia el JWT de memoria y de localStorage.
 * - Limpia también los datos de currentUser.
 */
function logout() {
  token.value = null
  currentUser.value = null
  currentUserEmail.value = null
  localStorage.removeItem('jwt')
  localStorage.removeItem('currentUserEmail')
}

/**
 * Hook que expone la API de autenticación para los componentes.
 */
export function useAuth() {
  return {
    API_BASE_URL,
    // estado
    token,
    currentUser,
    currentUserEmail,
    isAuthenticated,
    // acciones
    login,
    logout,
  }
}
