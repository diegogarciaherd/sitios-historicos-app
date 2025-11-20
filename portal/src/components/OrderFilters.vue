<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: String,
})

const emit = defineEmits(['update:modelValue'])

const orderBy = ref(props.modelValue || '')

// Sincronizar con props del padre
watch(
  () => props.modelValue,
  (newValue) => {
    orderBy.value = newValue
  },
)

// Emitir cambios
watch(orderBy, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2"> Ordenar por </label>
    <select
      v-model="orderBy"
      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
    >
      <option value="">Sin ordenar</option>
      <option value="name-asc">Nombre A-Z</option>
      <option value="name-desc">Nombre Z-A</option>
      <option value="latest">Más recientes primero</option>
      <option value="oldest">Más antiguos primero</option>
      <option value="most-visited">Más visitados</option>

      <option value="rating-5-1">Mejor rankeados</option>
      <option value="rating-1-5">Peor rankeados</option>
    </select>
  </div>
</template>
