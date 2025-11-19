// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

// Ojo: acá la idea es tener todas las rutas del portal público.
// Las views se cargan lazy donde tiene sentido, así no se baja
// todo el bundle de una sola vez.

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Página principal (landing)
    {
      path: '/',
      name: 'home',
      component: HomeView
    },

    // Listado de sitios históricos con filtros
    {
      path: '/sitios',
      name: 'sites-list',
      component: () => import('@/views/SitesListView.vue'),
      props: route => ({
        // paso query params como props para no acoplar la vista a $route
        query: route.query
      })
    },

    // Detalle de un sitio (se usa para ver info completa y reviews)
    {
      path: '/sitios/:id',
      name: 'site-detail',
      component: () => import('@/views/SiteDetailView.vue'),
      props: true
    },

    // Login público (acá el usuario obtiene el JWT)
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },

    // Mis sitios favoritos (solo accesible estando logueado)
    {
      path: '/favoritos',
      name: 'favorites',
      component: () => import('@/views/FavoritesView.vue')
    }
  ]
})

export default router
