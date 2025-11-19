// src/composables/useAuth.js
/**
 * Manejo de autenticación en el portal público.
 *
 * - Hace login contra la API de Flask: POST /api/auth/login
 * - Guarda el JWT en localStorage.
 * - Expone estado reactivo para saber si hay usuario logueado.
 */

import { ref, computed, watchEffect } from 'vue'
import axios from 'axios'

// URL base de la API (sin /api al final, lo agregamos después en cada llamada)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000'

// Estado global simple en memoria
const token = ref(localStorage.getItem('jwt') || null)
const currentUser = ref(
  token.value
    ? { email: localStorage.getItem('currentUserEmail') || '' }
    : null
)

const isAuthenticated = computed(() => !!token.value)

/**
 * Setea / limpia el header Authorization global de axios
 */
function setAxiosAuthHeader (value) {
  if (value) {
    axios.defaults.headers.common.Authorization = `Bearer ${value}`
  } else {
    delete axios.defaults.headers.common.Authorization
  }
}

// Inicializamos el header al levantar la app
setAxiosAuthHeader(token.value)

// Cada vez que cambie el token, actualizamos el header
watchEffect(() => {
  setAxiosAuthHeader(token.value)
})

/**
 * Hace login contra la API pública.
 *
 * Llama a:
 *   POST {API_BASE_URL}/api/auth/login
 * body:
 *   { email, password }
 */
async function login (email, password) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      email,
      password
    })

    const jwt = response.data.access_token

    if (!jwt) {
      return {
        ok: false,
        message: 'El servidor no devolvió un token válido.'
      }
    }

    token.value = jwt
    currentUser.value = {
      id: response.data.user_id,
      email
    }

    localStorage.setItem('jwt', jwt)
    localStorage.setItem('currentUserEmail', email)

    return { ok: true }
  } catch (error) {
    console.error('Error en login:', error)

    let message = 'No se pudo iniciar sesión.'

    if (error.response?.status === 401) {
      message = 'Credenciales inválidas.'
    } else if (error.response?.data?.error?.message) {
      message = error.response.data.error.message
    }

    return {
      ok: false,
      message
    }
  }
}

/**
 * Cierra la sesión del usuario:
 * - Limpia el JWT de memoria y de localStorage.
 * - Limpia también los datos de currentUser.
 */
function logout () {
  token.value = null
  currentUser.value = null
  localStorage.removeItem('jwt')
  localStorage.removeItem('currentUserEmail')
}

/**
 * Hook que expone la API de autenticación para los componentes.
 */
export function useAuth () {
  return {
    API_BASE_URL,
    // estado
    token,
    currentUser,
    isAuthenticated,
    // acciones
    login,
    logout
  }
}
