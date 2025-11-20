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
  const initialLat = route.query.lat ? String(route.query.lat) : ''
  const initialLng = route.query.lng ? String(route.query.lng) : ''
  const initialRadius = route.query.radius ? String(route.query.radius) : ''
  const initialOrderBy = route.query.order_by ? String(route.query.order_by) : ''
  const initialTags = route.query.tags
    ? String(route.query.tags)
        .split(',')
        .map((name) => ({ name: name.trim() }))
        .filter((t) => t.name)
    : []
  const initialPage = route.query.page ? Number(route.query.page) : 1

  const searchTerm = ref(initialSearch)
  const page = ref(initialPage)

  const appliedFilters = ref({
    city: initialCity,
    province: initialProvince,
    tags: initialTags,
    order_by: initialOrderBy,
    lat: initialLat,
    lng: initialLng,
    radius: initialRadius,
  })

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
      const tagNames = appliedFilters.value.tags
        .map((tag) => {
          if (typeof tag === 'string') return tag
          return tag?.name || ''
        })
        .filter((name) => name)

      if (tagNames.length > 0) {
        query.tags = tagNames.join(',')
      }
    }

    if (appliedFilters.value.order_by) {
      query.order_by = appliedFilters.value.order_by
    }


    if (appliedFilters.value.lat) {
      query.lat = appliedFilters.value.lat
    }
    if (appliedFilters.value.lng) {
      query.lng = appliedFilters.value.lng
    }
    if (appliedFilters.value.radius) {
      query.radius = appliedFilters.value.radius
    }

    if (page.value && page.value >= 1) {
      query.page = page.value
    }

    router.replace({
      query: Object.keys(query).length > 0 ? query : {},
    })
  }

  const combinedFilters = computed(() => {
    const combined = { ...appliedFilters.value }
    if (searchTerm.value) {
      combined.search = searchTerm.value
    }
    // Convertir tags a array de nombres para el backend
    if (combined.tags && Array.isArray(combined.tags) && combined.tags.length > 0) {
      combined.tags = combined.tags
        .map((tag) => {
          if (typeof tag === 'string') return tag
          return tag?.name || ''
        })
        .filter((name) => name)

      if (combined.tags.length === 0) {
        delete combined.tags
      }
    } else {
      delete combined.tags
    }

    // Eliminar valores vacíos
    Object.keys(combined).forEach((key) => {
      if (!combined[key] || (Array.isArray(combined[key]) && combined[key].length === 0)) {
        delete combined[key]
      }
    })

    
    if (combined.lat && combined.lng) {
  const mapOnly = {
    lat: combined.lat,
    lng: combined.lng,
  }

  if (combined.radius) mapOnly.radius = combined.radius
  if (combined.order_by) mapOnly.order_by = combined.order_by 

  return { ...mapOnly, page: page.value }

    }

    return combined
  })

  function handleSearch(searchValue) {
    searchTerm.value = searchValue

    if (siteFiltersRef.value) {
      const currentFilters = siteFiltersRef.value.getFilters()

      appliedFilters.value = {
        city: currentFilters.city || '',
        province: currentFilters.province || '',
        tags: currentFilters.tagsObjects || [],
        order_by: currentFilters.order_by || '',
      }
    } else {
    }

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
      tags: [],
      order_by: '',
    }
    syncToUrl()
  }

  function handlePageChange(newPage) {
    page.value = newPage
    syncToUrl()
  }

  watch(
    () => route.query,
    (newQuery) => {
      const newSearch = newQuery.search ? String(newQuery.search) : ''
      const newCity = newQuery.city ? String(newQuery.city) : ''
      const newProvince = newQuery.province ? String(newQuery.province) : ''
      const newOrderBy = newQuery.order_by ? String(newQuery.order_by) : ''
      const newTags = newQuery.tags
        ? String(newQuery.tags)
            .split(',')
            .map((name) => ({ name: name.trim() }))
            .filter((t) => t.name)
        : []

      const newLat = newQuery.lat ? String(newQuery.lat) : ''
      const newLng = newQuery.lng ? String(newQuery.lng) : ''
      const newRadius = newQuery.radius ? String(newQuery.radius) : ''

      if (newSearch !== searchTerm.value) {
        searchTerm.value = newSearch
      }
      if (newCity !== appliedFilters.value.city) {
        appliedFilters.value.city = newCity
      }
      if (newProvince !== appliedFilters.value.province) {
        appliedFilters.value.province = newProvince
      }
      if (newOrderBy !== appliedFilters.value.order_by) {
        appliedFilters.value.order_by = newOrderBy
      }

      const newPage = newQuery.page ? Number(newQuery.page) : 1
      if (newPage !== page.value) {
        page.value = newPage
      }

      const currentTagNames = appliedFilters.value.tags
        .map((t) => (typeof t === 'string' ? t : t.name))
        .sort()
      const newTagNames = newTags.map((t) => t.name).sort()
      if (JSON.stringify(currentTagNames) !== JSON.stringify(newTagNames)) {
        appliedFilters.value.tags = newTags
      }

      // Actualizar filtros de mapa
      if (newLat !== appliedFilters.value.lat) {
        appliedFilters.value.lat = newLat
      }
      if (newLng !== appliedFilters.value.lng) {
        appliedFilters.value.lng = newLng
      }
      if (newRadius !== appliedFilters.value.radius) {
        appliedFilters.value.radius = newRadius
      }
    },
    { deep: true },
  )


function goBackToList() {
  const queryParams = {}
  
  // Reconstruir los parámetros
  if (searchTerm.value) queryParams.search = searchTerm.value
  if (appliedFilters.value.city) queryParams.city = appliedFilters.value.city
  if (appliedFilters.value.province) queryParams.province = appliedFilters.value.province
  if (appliedFilters.value.order_by) queryParams.order_by = appliedFilters.value.order_by
  if (page.value && page.value > 1) queryParams.page = page.value
  
  // Tags
  if (appliedFilters.value.tags && appliedFilters.value.tags.length > 0) {
    const tagNames = appliedFilters.value.tags
      .map(tag => typeof tag === 'string' ? tag : tag?.name || '')
      .filter(name => name)
    if (tagNames.length > 0) {
      queryParams.tags = tagNames.join(',')
    }
  }
  
  // Parámetros de mapa
  if (appliedFilters.value.lat) queryParams.lat = appliedFilters.value.lat
  if (appliedFilters.value.lng) queryParams.lng = appliedFilters.value.lng
  if (appliedFilters.value.radius) queryParams.radius = appliedFilters.value.radius


  router.push({
    name: 'sites-list', 
    query: queryParams
  })
}

  return {
    page,
    searchTerm,
    searchBarRef,
    siteFiltersRef,
    appliedFilters,
    combinedFilters,
    handleSearch,
    handleClear,
    handlePageChange,
    goBackToList
  }
}
