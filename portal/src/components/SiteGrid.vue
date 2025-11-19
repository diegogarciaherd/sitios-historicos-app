<script setup>
import { ref, onMounted, watch } from 'vue'
import { getSites, getSitesNearby } from '@/api/sites'
import DetailedSiteCard from './DetailedSiteCard.vue'

const props = defineProps({
  siteFilters: {
    type: Object,
    default: () => ({}),
  },
  page: Number,
})

const emit = defineEmits(['change-page'])

const sites = ref([])
const perPage = 4
const totalPages = ref(1)
const loading = ref(false)

async function fetchSites() {
  loading.value = true
  try {
    // Si los filtros contienen lat y lng, hacemos una búsqueda estricta por mapa
    if (props.siteFilters && props.siteFilters.lat && props.siteFilters.lng) {
      try {
        const resp = await getSitesNearby({
          lat: props.siteFilters.lat,
          lng: props.siteFilters.lng,
          radius: props.siteFilters.radius || 5,
        })
        sites.value = resp.data || []
        totalPages.value = 1
        return
      } catch (err) {
        console.error('Error fetching nearby sites:', err)
        sites.value = []
        totalPages.value = 1
        return
      }
    }
    const response = await getSites({
      page: props.page,
      per_page: perPage,
      ...props.siteFilters,
    })
    sites.value = response.data || []
    totalPages.value = response.meta?.total_pages || 1
  } finally {
    loading.value = false
  }
}

// Recargar cuando cambien los filtros
watch(
  () => props.siteFilters,
  () => {
    emit('change-page', 1) // reset
    // Recargar inmediatamente cuando cambian los filtros
    fetchSites()
  },
  { deep: true },
)

watch(() => props.page, fetchSites)

function nextPage() {
  if (props.page < totalPages.value) {
    emit('change-page', props.page + 1)
  }
}

function prevPage() {
  if (props.page > 1) {
    emit('change-page', props.page - 1)
  }
}

onMounted(fetchSites)
</script>

<template>
  <div class="w-full flex flex-col gap-4 pb-4">
    <!-- Cuando se esta cargando los sitios -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div
          class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
        ></div>
        <p class="mt-2 text-gray-600">Cargando sitios...</p>
      </div>
    </div>

    <!-- Grid responsive: 1 col móvil, 2 tablet, 2 desktop -->
    <div
      v-else-if="sites.length > 0"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 sm:gap-6 w-full"
    >
      <DetailedSiteCard
        v-for="site in sites"
        :key="site.id"
        :site="site"
        @click="$router.push(`sitios/${site.id}`)"
        class="cursor-pointer"
      />
    </div>

    <!-- Estado vacío -->
    <div v-else-if="!loading" class="flex items-center justify-center py-12">
      <p class="text-gray-500 text-center">No se encontraron sitios para mostrar.</p>
    </div>

    <!-- Paginación: siempre visible -->
    <div
      v-if="!loading"
      class="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-gray-200"
    >
      <button
        @click="prevPage"
        :disabled="props.page === 1 || totalPages === 0"
        class="px-4 py-2 bg-gray-800 text-white rounded disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
      >
        Anterior
      </button>

      <span class="text-gray-700 font-medium">
        Página {{ props.page }} de {{ totalPages || 1 }}
      </span>

      <button
        @click="nextPage"
        :disabled="props.page >= totalPages || totalPages === 0"
        class="px-4 py-2 bg-gray-800 text-white rounded disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
      >
        Siguiente
      </button>
    </div>
  </div>
</template>
