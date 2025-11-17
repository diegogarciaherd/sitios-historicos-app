<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: ""
  }
})

const emit = defineEmits(["update:modelValue"])

const orders = [
  { label: "Fecha (más reciente)", value: "latest" },
  { label: "Fecha (más antiguo)", value: "oldest" },

  { label: "Nombre (A→Z)", value: "name-asc" },
  { label: "Nombre (Z→A)", value: "name-desc" },

  { label: "Mejor rankeados", value: "rating-5-1" },
  { label: "Peor rankeados", value: "rating-1-5" }
]
</script>

<template>
  <div class="w-full">
    <label class="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>

    <select
      class="border rounded-lg px-3 py-2 w-full"
      :value="modelValue"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="">Sin orden</option>

      <optgroup label="Fecha">
        <option value="latest">Más reciente</option>
        <option value="oldest">Más antiguo</option>
      </optgroup>

      <optgroup label="Nombre">
        <option value="name-asc">A → Z</option>
        <option value="name-desc">Z → A</option>
      </optgroup>

      <optgroup label="Ranking">
        <option value="rating-5-1">Mejor rankeados</option>
        <option value="rating-1-5">Peor rankeados</option>
      </optgroup>
    </select>
  </div>
</template>
