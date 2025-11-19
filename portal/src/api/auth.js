// src/api/auth.js
import api from './base'

/**
 * Realiza el login contra la API Flask.
 * Espera email y password, y devuelve el payload del backend:
 * { access_token, expires_in, user: { id, name, last_name, email } }
 */
export async function loginRequest(email, password) {
  const response = await api.post('/auth/login', {
    email,
    password,
  })
  return response.data
}
