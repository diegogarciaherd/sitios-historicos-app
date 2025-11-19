<script setup>
import Tag from '@/components/Tag.vue'

const props = defineProps({
  tags: {
    type: Array,
    required: true,
  },
  selectedTags: {
    type: Array,
    required: true,
  }
})

const emit = defineEmits(['update:selectedTags'])

function toggleTag(tag) {
  const exists = props.selectedTags.some(t => t.id === tag.id)

  let updated
  if (exists) {
    updated = props.selectedTags.filter(t => t.id !== tag.id)
  } else {
    updated = [...props.selectedTags, tag]
  }

  emit('update:selectedTags', updated)
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <Tag
      v-for="tag in tags"
      :key="tag.id"
      :tag="tag"
      :selected-tags="selectedTags"
      @toggle="toggleTag"
    />
  </div>
</template>
