<script setup>
import { ref, onMounted, watch } from 'vue'
import { getSitesFixed } from '@/api/sites'
import SiteCard from './SiteCard.vue'

const props = defineProps({
  siteFilters: {
    type: Object,
    default: () => ({})
  }
})

const sites = ref([])
const page = ref(1)
const perPage = 4
const totalPages = ref(1)
const loading = ref(false)

async function fetchSites() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: perPage,
      ...props.siteFilters
    }
    const response = await getSitesFixed(params)
    console.log('Response in SiteGrid:', response)
    if (response && response.data) {
      sites.value = response.data
      totalPages.value = response.meta?.total_pages || 1
    } else {
      console.error('Invalid response format:', response)
      sites.value = []
      totalPages.value = 1
    }
  } catch(error) {
    console.error("Error fetching sites:", error)
    sites.value = []
    totalPages.value = 1
  }
  finally {
    loading.value = false
  }
}

// Recargar cuando cambien los filtros
watch(() => props.siteFilters, () => {
  page.value = 1 // Resetear a la primera página
  fetchSites()
}, { deep: true })

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    fetchSites()
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    fetchSites()
  }
}

onMounted(fetchSites)
</script>

<template>
  <div class="w-full flex flex-col gap-4 pb-4">
    
    <!-- Cuando se esta cargando los sitios -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Cargando sitios...</p>
      </div>
    </div>

    <!-- Grid responsive: 1 col móvil, 2 tablet, 2 desktop -->
    <div v-else-if="sites.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 sm:gap-6 w-full">
      <SiteCard v-for="site in sites" :key="site.id" :site="site" />
    </div>

    <!-- Estado vacío -->
    <div v-else-if="!loading" class="flex items-center justify-center py-12">
      <p class="text-gray-500 text-center">No se encontraron sitios para mostrar.</p>
    </div>

    <!-- Paginación: siempre visible -->
    <div v-if="!loading" class="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-gray-200">
      <button 
        @click="prevPage" 
        :disabled="page === 1 || totalPages === 0"
        class="px-4 py-2 bg-gray-800 text-white rounded disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
      >
        Anterior
      </button>
      
      <span class="text-gray-700 font-medium">
        Página {{ page }} de {{ totalPages || 1 }}
      </span>
      
      <button 
        @click="nextPage" 
        :disabled="page >= totalPages || totalPages === 0"
        class="px-4 py-2 bg-gray-800 text-white rounded disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
      >
        Siguiente
      </button>
    </div>

  </div>
</template>