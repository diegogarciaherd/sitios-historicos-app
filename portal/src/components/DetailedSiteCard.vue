<script setup>
import { defineProps } from 'vue'
const props = defineProps({
  site: {
    type: Object,
    required: true,
    // { nombre, descripcion, image, ciudad }
  },
})
</script>

<template>
  <div
    class="site-card rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 w-60 h-80"
  >
    <img
      :src="site.image"
      :alt="site.nombre"
      class="h-[50%] object-cover z-0 mask-b-from-50% mask-to-100%"
    />
    <div
      class="p-4 absolute bottom-0 rounded-lg bg-linear-to-t from-gray-800 to-transparent w-full z-10"
    >
      <h2 class="text-xl font-semibold text-white mb-2 z-10">{{ site.nombre }}</h2>
      <p class="text-white mb-4">{{ site.descripcion }}</p>
    </div>
  </div>
</template>

<style scoped>
.site-card {
  background-color: white;
}
</style>
