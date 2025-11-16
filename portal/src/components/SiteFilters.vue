<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  appliedFilters: {
    type: Object,
    default: () => ({
      city: '',
      province: ''
    })
  }
})

const emit = defineEmits(['clear'])

const isOpen = ref(false)
const city = ref(props.appliedFilters.city || '')
const province = ref(props.appliedFilters.province || '')

// Sincronizar con props aplicados (para reflejar valores de URL)
watch(() => props.appliedFilters, (newFilters) => {
  city.value = newFilters.city || ''
  province.value = newFilters.province || ''
}, { deep: true })

// Obtener filtros actuales sin emitir
function getFilters() {
  const filters = {}
  if (city.value) filters.city = city.value
  if (province.value) filters.province = province.value
  return filters
}

function clearFilters() {
  city.value = ''
  province.value = ''
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
          <input
            id="province"
            v-model="province"
            type="text"
            placeholder="Filtrar por provincia..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
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

