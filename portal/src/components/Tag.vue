<template>
    <button
      type="button"
      @click="$emit('toggle', tag)"
      :class="[
        'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium transition-colors',
        isSelected 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-400/10 text-gray-300 hover:bg-gray-400/20'
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
  