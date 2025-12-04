<template>
    <button
      type="button"
      @click="handleClick"
      :class="[
        'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium transition-colors',
        isSelected 
          ? 'badge badge-success' 
          : 'badge --badge-color'
      ]"
    >
      {{ tag.name }}
    </button>
  </template>
  
  <script setup>
  import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
  
  const props = defineProps({
    tag: {
      type: Object,
      required: true,
    },
    selectedTags: {
      type: Array,
      default: () => []
    }
  })
  
  const emit = defineEmits(['toggle'])
const router = useRouter()
const route = useRoute()

function handleClick() {
  // Emitir el evento toggle para no romper consumidores existentes
  emit('toggle', props.tag)

  // Navegar al listado con este tag como filtro (reemplaza otros tags)
  const newQuery = { ...route.query }
  // usar el nombre del tag en el query param 'tags'
  newQuery.tags = String(props.tag.name)
  // resetear pagina
  newQuery.page = 1

  router.push({ name: 'sites-list', query: newQuery })
}
  
  const isSelected = computed(() => {
    return props.selectedTags.some(t => 
      (typeof t === 'object' && t.id === props.tag.id) || 
      (typeof t === 'string' && t === props.tag.name)
    )
  })
  </script>
  