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
  // Tags desde query params (string separado por comas de nombres)
  const initialTags = query.tags 
    ? String(query.tags).split(',').map(name => ({ name: name.trim() })).filter(t => t.name)
    : []
  const initialPage = query.page ? Number(query.page) : 1

  // Estado de búsqueda y filtros aplicados
  const searchTerm = ref(initialSearch)
  const searchBarRef = ref(null)
  const siteFiltersRef = ref(null)
  const page = ref(initialPage)
  const appliedFilters = ref({
    city: initialCity,
    province: initialProvince,
    tags: initialTags,

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
    if (appliedFilters.value.tags && appliedFilters.value.tags.length > 0) {
      // Convertir tags a string separado por comas (nombres)
      query.tags = appliedFilters.value.tags
        .map(tag => typeof tag === 'string' ? tag : tag.name)
        .join(',')
    }
    
    if (page.value && page.value >= 1) {
      query.page = page.value
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
    // Convertir tags a array de nombres para el backend
    if (combined.tags && Array.isArray(combined.tags) && combined.tags.length > 0) {
      combined.tags = combined.tags.map(tag => 
        typeof tag === 'string' ? tag : tag.name
      )
    } else {
      delete combined.tags
    }
    // Eliminar valores vacíos
    Object.keys(combined).forEach(key => {
      if (!combined[key] || (Array.isArray(combined[key]) && combined[key].length === 0)) {
        delete combined[key]
      }
    })
    return combined
  })

  // Handler de búsqueda: combina búsqueda con filtros actuales
  function handleSearch(searchValue) {
  searchTerm.value = searchValue

  // Tomar filtros desde el componente SiteFilters
  if (siteFiltersRef.value) {
    const currentFilters = siteFiltersRef.value.getFilters()
    appliedFilters.value = {
      city: currentFilters.city || '',
      province: currentFilters.province || '',
      tags: currentFilters.tagsObjects || []
    }
  }

  // Resetear página SIEMPRE
  page.value = 1

  syncToUrl()
}


  function handleClear() {
    searchTerm.value = ''
    searchBarRef.value?.clear()
    siteFiltersRef.value?.clear()
    appliedFilters.value = {
      city: '',
      province: '',
      tags: []
    }
    syncToUrl()
    
  }

  function handlePageChange(newPage) {
  page.value = newPage
  syncToUrl()
}

  // Sincronizar cuando cambien los query params (navegación del navegador)
  watch(() => route.query, (newQuery) => {
    const newSearch = newQuery.search ? String(newQuery.search) : ''
    const newCity = newQuery.city ? String(newQuery.city) : ''
    const newProvince = newQuery.province ? String(newQuery.province) : ''
    const newTags = newQuery.tags

      ? String(newQuery.tags).split(',').map(name => ({ name: name.trim() })).filter(t => t.name)
      : []

    if (newSearch !== searchTerm.value) {
      searchTerm.value = newSearch
    }
    if (newCity !== appliedFilters.value.city) {
      appliedFilters.value.city = newCity
    }
    if (newProvince !== appliedFilters.value.province) {
      appliedFilters.value.province = newProvince
    }

    const newPage = newQuery.page ? Number(newQuery.page) : 1
    if (newPage !== page.value) {
      page.value = newPage
    }
    // Comparar tags por nombres
    const currentTagNames = appliedFilters.value.tags.map(t => typeof t === 'string' ? t : t.name).sort()
    const newTagNames = newTags.map(t => t.name).sort()
    if (JSON.stringify(currentTagNames) !== JSON.stringify(newTagNames)) {
      appliedFilters.value.tags = newTags
    }
  }, { deep: true })

  return {
    page,
    searchTerm,
    searchBarRef,
    siteFiltersRef,
    appliedFilters,
    combinedFilters,
    handleSearch,
    handleClear,
    handlePageChange
  }
}
