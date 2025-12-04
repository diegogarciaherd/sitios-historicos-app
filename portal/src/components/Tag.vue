<template>
    <button
      type="button"
      @click.stop="handleClick"
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
    ,
    navigate: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['toggle'])
const router = useRouter()
const route = useRoute()

function handleClick() {
  // Emitir el evento toggle para no romper consumidores existentes
  emit('toggle', props.tag)

  // Solo navegar si el consumidor lo pidió explícitamente
  if (props.navigate) {
    const newQuery = { ...route.query }
    newQuery.tags = String(props.tag.name)
    newQuery.page = 1
    router.push({ name: 'sites-list', query: newQuery })
  }
}
  
  const isSelected = computed(() => {
    return props.selectedTags.some(t => 
      (typeof t === 'object' && t.id === props.tag.id) || 
      (typeof t === 'string' && t === props.tag.name)
    )
  })
  </script>
  