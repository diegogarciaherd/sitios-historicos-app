<script setup>
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
  class="site-card relative rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 w-full aspect-[16/10] sm:aspect-[16/9]"
>
  <img
    :src="site.image"
    :alt="site.nombre"
    class="absolute inset-0 w-full h-full object-cover z-0"
  />

  <div
    class="absolute bottom-0 p-4 bg-gradient-to-t from-black/70 to-transparent w-full z-10"
  >
    <h2 class="text-base lg:text-lg font-semibold text-white mb-1">
      {{ site.nombre }}
    </h2>
    <p class="text-sm lg:text-base text-white line-clamp-2">
      {{ site.descripcionBreve }}
    </p>
    <p class="text-sm lg:text-lg text-white mb-2"> {{ site.ciudad }}</p>
    <p class="text-sm lg:text-lg text-white mb-2"> {{ site.provincia }}</p>
  </div>
</div>
</template>

<style scoped>
.site-card {
  background-color: #222;
}
</style>
