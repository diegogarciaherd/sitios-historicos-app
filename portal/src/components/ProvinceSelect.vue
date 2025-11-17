<script setup>
const props = defineProps({
  modelValue: String
})

const emit = defineEmits(['update:modelValue'])

const provinces = [
  "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
  "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones",
  "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
  "Santiago del Estero", "Tierra del Fuego", "Tucumán"
]

function updateValue(e) {
  emit("update:modelValue", e.target.value)
}
</script>

<template>
  <select
    :value="modelValue"
    @change="updateValue"
    class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
  >
    <option value="">Todas</option>
    <option v-for="p in provinces" :key="p" :value="p">
      {{ p }}
    </option>
  </select>
</template>
