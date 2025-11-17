<template>
  <div class="space-y-4">
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
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["search", "update:modelValue"]);

const searchTerm = ref(props.modelValue);

// Sincroniza modelValue solo si el padre lo cambia
watch(
  () => props.modelValue,
  (newValue) => {
    searchTerm.value = newValue;
  }
);

function handleSearch() {
  emit("update:modelValue", searchTerm.value); // actualiza el padre SOLO al confirmar
  emit("search", searchTerm.value); // dispara la búsqueda
}

defineExpose({
  clear: () => {
    searchTerm.value = "";
  },
});
</script>
