import HomeView from '@/views/HomeView.vue'
import SitesListView from '@/views/SitesListView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/sitios',
      name: 'sites-list',
      component: () => import('@/views/SitesListView.vue'),
      props: route => ({
        query: route.query
      })
    }
    
  ],

})

export default router
