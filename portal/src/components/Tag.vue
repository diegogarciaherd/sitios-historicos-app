<template>
    <button
      type="button"
      @click="$emit('toggle', tag)"
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
  
  defineEmits(['toggle'])
  
  const isSelected = computed(() => {
    return props.selectedTags.some(t => 
      (typeof t === 'object' && t.id === props.tag.id) || 
      (typeof t === 'string' && t === props.tag.name)
    )
  })
  </script>
  