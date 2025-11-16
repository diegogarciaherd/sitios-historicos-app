<template>
    <div class="space-y-4">
      <label for="search" class="block text-sm font-medium text-gray-700 mb-2">
        Buscar sitio histórico
      </label>
  
      <div class="flex gap-2">
  <input
    id="search"
    v-model="searchTerm"
    type="text"
    placeholder="Buscar por nombre o descripción..."
    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-950"
    @keyup.enter="handleSearch"
  />

  <button
    @click="handleSearch"
    class="px-4 py-2 bg-blue-950 text-white rounded-lg hover:bg-blue-900 transition-colors"
  >
    Buscar
  </button>
</div>
</div>
</template>
  


<script setup>
import { ref } from 'vue'

const emit = defineEmits(['search'])

const searchTerm = ref('')

function handleSearch() {
  emit('search', searchTerm.value)
}

defineExpose({
  clear: () => {
    searchTerm.value = ''
  }
})
</script>