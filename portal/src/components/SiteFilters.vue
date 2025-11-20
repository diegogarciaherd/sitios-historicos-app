<script setup>
import { ref, watch, onMounted } from 'vue'
import TagFilter from './TagFilter.vue'
import { getAllTags } from '@/api/tags'
import ProvinceSelect from './ProvinceSelect.vue'
import OrderFilters from './OrderFilters.vue'

const props = defineProps({
  appliedFilters: {
    type: Object,
    default: () => ({
      city: '',
      province: '',
      tags: [],
      order_by: '',
    }),
  },
})

const emit = defineEmits(['clear'])

const city = ref(props.appliedFilters.city || '')
const province = ref(props.appliedFilters.province || '')
const selectedTags = ref(props.appliedFilters.tags || [])
const orderBy = ref(props.appliedFilters.order_by || '')
const favorites = ref(props.appliedFilters.favorites || false)
const availableTags = ref([])

const isOpen = ref(false)
onMounted(async () => {
  const res = await getAllTags()
  availableTags.value = res.results || []

  if (props.appliedFilters.tags?.length > 0) {
    selectedTags.value = props.appliedFilters.tags
      .map((tagObj) => {
        if (tagObj && tagObj.id) return tagObj
        if (tagObj && tagObj.name) {
          const found = availableTags.value.find((t) => t.name === tagObj.name)
          return found || null
        }
        return null
      })
      .filter(Boolean)
  }
})

watch(
  () => props.appliedFilters,
  (newFilters) => {
    city.value = newFilters.city || ''
    province.value = newFilters.province || ''
    orderBy.value = newFilters.order_by || ''
    favorites.value = newFilters.favorites || false 

    if (newFilters.tags?.length > 0) {
      selectedTags.value = newFilters.tags
        .map((tagObj) => {
          if (tagObj && tagObj.id) return tagObj
          if (tagObj && tagObj.name) {
            const found = availableTags.value.find((t) => t.name === tagObj.name)
            return found || null
          }
          return null
        })
        .filter(Boolean)
    } else {
      selectedTags.value = []
    }
  },
  { deep: true },
)

function getFilters() {
  const filters = {
    city: city.value || '',
    province: province.value || '',
    order_by: orderBy.value || '',
    tagsObjects: selectedTags.value || [],
    tags: (selectedTags.value || [])
      .map((t) => {
        if (typeof t === 'string') return t
        return t?.name || ''
      })
      .filter((name) => name),
  }

  return filters
}

function clearFilters() {
  city.value = ''
  province.value = ''
  orderBy.value = ''
  selectedTags.value = []
  favorites.value = false
  emit('clear')
}

defineExpose({
  getFilters,
  clear: clearFilters,
})
</script>

<template>
  <div class="w-full">
    <!-- Botón para móvil -->
    <button
      @click="isOpen = !isOpen"
      class="md:hidden w-full flex items-center justify-between p-4 bg-gray-800 text-white rounded-lg mb-4 hover:bg-gray-700 transition-colors"
    >
      <span class="font-medium">Buscar y Filtrar</span>
      <svg
        :class="['w-5 h-5 transition-transform', isOpen ? 'rotate-180' : '']"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Panel de filtros -->
    <div :class="['md:block', isOpen ? 'block' : 'hidden']">
      <div class="space-y-4 border border-gray-300 rounded-lg p-4">
        <h3 class="text-lg font-bold text-center text-gray-700 mb-2">Filtros</h3>

        <!-- Ciudad -->
        <div>
          <label for="city" class="block text-sm font-medium text-gray-700 mb-2"> Ciudad </label>
          <input
            id="city"
            v-model="city"
            type="text"
            placeholder="Filtrar por ciudad..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Provincia -->
        <div>
          <label for="province" class="block text-sm font-medium text-gray-700 mb-2">
            Provincia
          </label>
          <ProvinceSelect v-model="province" />
        </div>

        <!-- ✅ OrderSelector simplificado -->
        <OrderFilters v-model="orderBy" />

        <!-- Filtro de Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"> Tags </label>
          <TagFilter
            v-if="availableTags.length > 0"
            :tags="availableTags"
            :selected-tags="selectedTags"
            @update:selected-tags="selectedTags = $event"
          />
          <p v-else class="text-sm text-gray-500">Cargando tags...</p>
        </div>

        <!-- Botón de limpiar -->
        <div class="pt-2">
          <button
            @click="clearFilters"
            class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Limpiar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
