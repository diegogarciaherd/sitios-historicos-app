<script setup>
const props = defineProps({
  site: {
    type: Object,
    required: true,
    // { nombre, descripcionBreve, image, ciudad }
  },
})
</script>

<template>
  <div
    class="site-card rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 w-35 h-50 lg:w-80 lg:h-120"
  >
    <img
      :src="site.image"
      :alt="site.nombre"
      class="h-full object-cover position-absolute z-0 mask-b-from-50% mask-to-100%"
    />
    <div
      class="p-4 absolute bottom-0 rounded-lg bg-linear-to-t from-gray-800 to-transparent w-full z-10"
    >
      <h2 class="text-sm lg:text-xl font-semibold text-white mb-2 z-10">{{ site.nombre }}</h2>
      <p class="text-xs lg:text-base text-white mb-4">{{ site.descripcionBreve }}</p>
    </div>
  </div>
</template>

<style scoped>
.site-card {
  background-color: #222;
}
</style>
