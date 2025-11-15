<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

const isOpen = ref(false)
const searchTerm = ref(props.modelValue.search || '')
const city = ref(props.modelValue.city || '')
const province = ref(props.modelValue.province || '')

const filters = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

function applyFilters() {
  const newFilters = {
    search: searchTerm.value,
    city: city.value,
    province: province.value
  }
  // Eliminar filtros vacíos
  Object.keys(newFilters).forEach(key => {
    if (!newFilters[key]) delete newFilters[key]
  })
  filters.value = newFilters
  emit('search', newFilters)
  // Cerrar en móvil después de aplicar
  if (window.innerWidth < 768) {
    isOpen.value = false
  }
}

function clearFilters() {
  searchTerm.value = ''
  city.value = ''
  province.value = ''
  filters.value = {}
  emit('search', {})
  if (window.innerWidth < 768) {
    isOpen.value = false
  }
}
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
        'bg-white rounded-lg shadow-md p-4 md:p-6',
        'md:block',
        isOpen ? 'block' : 'hidden'
      ]"
    >
      <h3 class="text-lg font-semibold mb-4 text-gray-800 hidden md:block">
        Buscar y Filtrar
      </h3>

      <div class="space-y-4">
        <!-- Buscador -->
        <div>
          <label for="search" class="block text-sm font-medium text-gray-700 mb-2">
            Buscar sitio
          </label>
          <input
            id="search"
            v-model="searchTerm"
            type="text"
            placeholder="Buscar por nombre o descripción..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @keyup.enter="applyFilters"
          />
        </div>

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
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @keyup.enter="applyFilters"
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
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @keyup.enter="applyFilters"
          />
        </div>

        <!-- Botones de acción -->
        <div class="flex flex-col sm:flex-row gap-2 pt-2">
          <button
            @click="applyFilters"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Aplicar Filtros
          </button>
          <button
            @click="clearFilters"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Limpiar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

