import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAllTags } from '@/api/tags'

export function useSiteSearch() {
  const route = useRoute()
  const router = useRouter()

  const searchBarRef = ref(null)
  const siteFiltersRef = ref(null)

  const availableTags = ref([])

  onMounted(async () => {
    const res = await getAllTags()
    availableTags.value = res.results || []

    // reconstruir tags iniciales desde URL
    const tagNames = route.query.tags ? String(route.query.tags).split(',') : []
    appliedFilters.value.tags = buildTagObjectsFromNames(tagNames)
  })

  function buildTagObjectsFromNames(names) {
    return names
      .map(n => n.trim())
      .map(name => availableTags.value.find(t => t.name === name))
      .filter(Boolean)
  }

  const initialSearch = route.query.search || ''
  const initialCity = route.query.city || ''
  const initialProvince = route.query.province || ''
  const initialOrderBy = route.query.order_by || ''

  const searchTerm = ref(initialSearch)
  const page = ref(Number(route.query.page) || 1)
  const orderBy = ref(initialOrderBy)

  const appliedFilters = ref({
    city: initialCity,
    province: initialProvince,
    tags: [],
    order_by: initialOrderBy
  })

  function syncToUrl() {
    const q = {}

    if (searchTerm.value) q.search = searchTerm.value
    if (appliedFilters.value.city) q.city = appliedFilters.value.city
    if (appliedFilters.value.province) q.province = appliedFilters.value.province
    if (appliedFilters.value.tags.length > 0)
      q.tags = appliedFilters.value.tags.map(t => t.name).join(',')

    if (orderBy.value) q.order_by = orderBy.value
    q.page = page.value

    router.replace({ query: q })
  }

  const combinedFilters = computed(() => {
    const f = { ...appliedFilters.value }

    if (searchTerm.value) f.search = searchTerm.value
    if (orderBy.value) f.order_by = orderBy.value

    if (f.tags?.length > 0) {
      f.tags = f.tags.map(t => t.name)
    } else {
      delete f.tags
    }

    Object.keys(f).forEach(k => {
      if (!f[k] || (Array.isArray(f[k]) && f[k].length === 0)) {
        delete f[k]
      }
    })

    return f
  })

  function handleSearch(val) {
    searchTerm.value = val

    const current = siteFiltersRef.value.getFilters()
    appliedFilters.value = {
      city: current.city || '',
      province: current.province || '',
      tags: current.tagsObjects || [],
      order_by: current.order_by || ''
    }

    page.value = 1
    syncToUrl()
  }

  function handleClear() {
    searchTerm.value = ''
    orderBy.value = ''
    appliedFilters.value = { city: '', province: '', tags: [], order_by: '' }
    syncToUrl()
  }

  function handlePageChange(newPage) {
    page.value = newPage
    syncToUrl()
  }

  function handleOrderChange(newOrder) {
    orderBy.value = newOrder
    page.value = 1
    syncToUrl()
  }

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
    handlePageChange,
    handleOrderChange
  }
}
