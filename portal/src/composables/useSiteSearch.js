import { ref, computed } from 'vue'

export function useSiteSearch() {
  // Estado de búsqueda y filtros aplicados
  const searchTerm = ref('')
  const searchBarRef = ref(null)
  const siteFiltersRef = ref(null)
  const appliedFilters = ref({
    city: '',
    province: ''
  })

  // Filtros combinados para pasar a SiteGrid (solo se actualizan al buscar)
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
  }

  function handleClear() {
    searchTerm.value = ''
    searchBarRef.value?.clear()
    siteFiltersRef.value?.clear()
    appliedFilters.value = {
      city: '',
      province: ''
    }
  }

  return {
    searchBarRef,
    siteFiltersRef,
    appliedFilters,
    combinedFilters,
    handleSearch,
    handleClear
  }
}

