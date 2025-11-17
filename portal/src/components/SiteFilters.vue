<script setup>
import { ref, watch, onMounted } from 'vue'
import TagFilter from './TagFilter.vue'
import { getAllTags } from '@/api/tags'
import ProvinceSelect from './ProvinceSelect.vue'
const props = defineProps({
  appliedFilters: {
    type: Object,
    default: () => ({
      city: '',
      province: '',
      tags: []
    })
  }
})

const emit = defineEmits(['clear'])

const isOpen = ref(false)
const city = ref(props.appliedFilters.city || '')
const province = ref(props.appliedFilters.province || '')
const selectedTags = ref(props.appliedFilters.tags || [])
const availableTags = ref([])

// Cargar tags disponibles
onMounted(async () => {
  availableTags.value = await getAllTags()
})

// Sincronizar con props aplicados (para reflejar valores de URL)
watch(() => props.appliedFilters, (newFilters) => {
  city.value = newFilters.city || ''
  province.value = newFilters.province || ''
  // Convertir tags desde URL (objetos con name) a objetos con id si están disponibles
  if (newFilters.tags && newFilters.tags.length > 0) {
    selectedTags.value = newFilters.tags.map(tag => {
      if (typeof tag === 'string') {
        // Buscar tag por nombre en availableTags
        const found = availableTags.value.find(t => t.name === tag)
        return found || { name: tag }
      }
      // Si ya es un objeto, buscar por nombre para obtener el id
      const found = availableTags.value.find(t => t.name === tag.name)
      return found || tag
    })
    
  } else {
    selectedTags.value = []
  }
}, { deep: true })

// Obtener filtros actuales sin emitir
function getFilters() {
  const filters = {}
  if (city.value) filters.city = city.value
  if (province.value) filters.province = province.value
  if (selectedTags.value && selectedTags.value.length > 0) {
    // Mantener tags como objetos para el estado, pero convertir a nombres para el backend
    filters.tags = selectedTags.value.map(tag => 
      typeof tag === 'string' ? tag : tag.name
    )
  }
  return { ...filters, tagsObjects: selectedTags.value }
}

function clearFilters() {
  city.value = ''
  province.value = ''
  selectedTags.value = []
  emit('clear')
  if (window.innerWidth < 768) {
    isOpen.value = false
  }
}

// Exponer método para obtener filtros desde fuera
defineExpose({
  getFilters,
  clear: clearFilters
})
</script>

<template>
  <div class="w-full">
    <!-- Boton para abrir el panel de filtros en movil y cuando se achica la pantalla -->
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

    <!-- Panel de filtros: acordeon en movil, siempre visible en desktop -->
    <div
      :class="[
        'md:block',
        isOpen ? 'block' : 'hidden'
      ]"
    >
      <div class="space-y-4 border border-gray-300 rounded-lg p-4">
        <h3 class="text-lg font-bold text-center text-gray-700 mb-2">
          Filtros
        </h3>
        
        <!-- Ciudad -->
        <div>
          <label for="city" class="block text-sm font-medium text-gray-700 mb-2">
            Ciudad
          </label>
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
          <ProvinceSelect 
          v-model="province" />
        </div>

        <!-- Filtro de Tags -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
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

