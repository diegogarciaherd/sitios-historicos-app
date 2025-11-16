import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useSiteSearch() {
  const route = useRoute()
  const router = useRouter()

  // Inicializar desde query params si existen
  const query = route.query
  const initialSearch = query.search ? String(query.search) : ''
  const initialCity = query.city ? String(query.city) : ''
  const initialProvince = query.province ? String(query.province) : ''

  // Estado de búsqueda y filtros aplicados
  const searchTerm = ref(initialSearch)
  const searchBarRef = ref(null)
  const siteFiltersRef = ref(null)
  const appliedFilters = ref({
    city: initialCity,
    province: initialProvince
  })

  // Sincronizar estado con URL (solo valores no vacíos)
  function syncToUrl() {
    const query = {}
    if (searchTerm.value) {
      query.search = searchTerm.value
    }
    if (appliedFilters.value.city) {
      query.city = appliedFilters.value.city
    }
    if (appliedFilters.value.province) {
      query.province = appliedFilters.value.province
    }

    // Usar replace para no agregar al historial en cada cambio
    router.replace({
      query: Object.keys(query).length > 0 ? query : {}
    })
  }

  // Filtros combinados para pasar a SiteGrid
  const combinedFilters = computed(() => {
    const combined = { ...appliedFilters.value }
    if (searchTerm.value) {
      combined.search = searchTerm.value
    }
    // Eliminar valores vacíos
    Object.keys(combined).forEach(key => {
      if (!combined[key]) delete combined[key]
    })
    return combined
  })

  // Handler de búsqueda: combina búsqueda con filtros actuales
  function handleSearch(searchValue) {
    searchTerm.value = searchValue
    // Obtener filtros actuales de SiteFilters y aplicarlos
    if (siteFiltersRef.value) {
      const currentFilters = siteFiltersRef.value.getFilters()
      appliedFilters.value = { ...currentFilters }
    }
    syncToUrl()
  }

  function handleClear() {
    searchTerm.value = ''
    searchBarRef.value?.clear()
    siteFiltersRef.value?.clear()
    appliedFilters.value = {
      city: '',
      province: ''
    }
    syncToUrl()
  }

  // Sincronizar cuando cambien los query params (navegación del navegador)
  watch(() => route.query, (newQuery) => {
    const newSearch = newQuery.search ? String(newQuery.search) : ''
    const newCity = newQuery.city ? String(newQuery.city) : ''
    const newProvince = newQuery.province ? String(newQuery.province) : ''

    if (newSearch !== searchTerm.value) {
      searchTerm.value = newSearch
    }
    if (newCity !== appliedFilters.value.city) {
      appliedFilters.value.city = newCity
    }
    if (newProvince !== appliedFilters.value.province) {
      appliedFilters.value.province = newProvince
    }
  }, { deep: true })

  return {
    searchTerm,
    searchBarRef,
    siteFiltersRef,
    appliedFilters,
    combinedFilters,
    handleSearch,
    handleClear
  }
}
