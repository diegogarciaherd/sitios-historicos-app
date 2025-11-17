import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useSiteSearch() {
  const route = useRoute()
  const router = useRouter()

  const searchBarRef = ref(null)
  const siteFiltersRef = ref(null)

  const initialSearch = route.query.search ? String(route.query.search) : ''
  const initialCity = route.query.city ? String(route.query.city) : ''
  const initialProvince = route.query.province ? String(route.query.province) : ''
  const initialOrderBy = route.query.order_by ? String(route.query.order_by) : ''
  // Tags desde query params (string separado por comas de nombres)
  const initialTags = route.query.tags 
    ? String(route.query.tags).split(',').map(name => ({ name: name.trim() })).filter(t => t.name)
    : []
  const initialPage = route.query.page ? Number(route.query.page) : 1

  const searchTerm = ref(initialSearch)
  const page = ref(initialPage)
  const orderBy = ref(initialOrderBy)
  
  const appliedFilters = ref({
    city: initialCity,
    province: initialProvince,
    tags: initialTags,
    order_by: initialOrderBy
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
    
    if (orderBy.value) {
      query.order_by = orderBy.value
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
    if (orderBy.value) {
      combined.order_by = orderBy.value
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

  // Tomar filtros desde el componente SiteFilters (incluyendo orderBy)
  if (siteFiltersRef.value) {
    const currentFilters = siteFiltersRef.value.getFilters()
    appliedFilters.value = {
      city: currentFilters.city || '',
      province: currentFilters.province || '',
      tags: currentFilters.tagsObjects || [],
      order_by: currentFilters.order_by || ''
    }
    // Sincronizar orderBy del composable con el de los filtros
    if (currentFilters.order_by) {
      orderBy.value = currentFilters.order_by
    }
  }

  // Resetear página SIEMPRE
  page.value = 1

  syncToUrl()
}

  function handleClear() {
    searchTerm.value = ''
    orderBy.value = ''
    searchBarRef.value?.clear()
    siteFiltersRef.value?.clear()
    appliedFilters.value = {
      city: '',
      province: '',
      tags: [],
      order_by: ''
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
    const newOrderBy = newQuery.order_by ? String(newQuery.order_by) : ''

    if (newSearch !== searchTerm.value) {
      searchTerm.value = newSearch
    }
    if (newCity !== appliedFilters.value.city) {
      appliedFilters.value.city = newCity
    }
    if (newProvince !== appliedFilters.value.province) {
      appliedFilters.value.province = newProvince
    }
    if (newOrderBy !== orderBy.value) {
      orderBy.value = newOrderBy
      appliedFilters.value.order_by = newOrderBy
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
    orderBy,
    searchBarRef,
    siteFiltersRef,
    appliedFilters,
    combinedFilters,
    handleSearch,
    handleClear,
    handlePageChange
  }
}
