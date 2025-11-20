// src/api/auth.js
import api from './base'

/**
 * Realiza el login contra la API Flask.
 * Espera email y password, y devuelve el payload del backend:
 * { access_token, expires_in, user: { id, name, last_name, email } }
 */

export async function loginRequest (email, password) {
  // Endpoint: POST /api/auth/
  const response = await api.post('/auth/', {
    email,
    password
  })
  return response.data
}

export async function handleCredentialResponse(response) {
  const token = response.credential;
  const res = await api.post("/auth/google", { token });
  const jwt = res.data.access_token;
  localStorage.setItem('jwt', jwt);
}
