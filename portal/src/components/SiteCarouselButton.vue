<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: null },
  value: { type: [String, Number, Boolean], required: true },
  label: { type: String, required: true },
  activeClass: { type: String, default: 'is-active' },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isActive = computed(() => props.modelValue === props.value)

function select() {
  if (!isActive.value) {
    emit('update:modelValue', props.value)
    emit('change', props.value)
  }
}
</script>

<template>
  <button
    type="button"
    class="toggle text-xs md:text-base w-fit md:w-auto"
    :class="{ [activeClass]: isActive }"
    role="radio"
    :aria-checked="isActive"
    @click="select"
  >
    {{ label }}
  </button>
</template>

<style scoped>
.toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1.2rem 2rem;
  border-radius: 999px;
  background-color: rgba(30, 41, 59, 0.35);
  color: #f8fafc;
  cursor: pointer;
  font-weight: 600;
  transition:
    background-color 220ms ease,
    transform 220ms ease,
    box-shadow 220ms ease;
  transform: scale(1);
}

.toggle:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.3);
}

.toggle.is-active {
  background: #38bdf8;
  transform: scale(1.05);
}
</style>
