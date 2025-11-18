<script setup>
const props = defineProps({
  site: {
    type: Object,
    required: true,
  },
})

const stateColors = {
  Bueno: 'bg-green-500',
  Regular: 'bg-yellow-500',
  Malo: 'bg-red-500',
}
</script>

<template>
  <div
    class="site-card relative rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 w-45 h-60 md:w-60 md:h-80"
  >
    <img
      :src="site.image"
      :alt="site.nombre"
      class="h-full w-full object-cover z-0 mask-b-from-50% mask-to-100%"
    />
    <div
      class="p-4 absolute bottom-0 text-start text-white rounded-lg bg-linear-to-t from-gray-800 to-transparent w-full z-10"
    >
      <h2 class="text-large font-semibold mb-2 z-10">{{ site.nombre }}</h2>
      <p class="mb-2 text-sm">{{ site.ciudad }} | {{ site.provincia }}</p>
      <span
        class="inline-block rounded-full text-xs py-1 px-2"
        :class="stateColors[site.estado] || 'bg-gray-500'"
        >{{ site.estado }}</span
      >
      <br />
      <div class="flex mt-2 space-2 min-h-14 max-h-14 items-end flex-wrap">
        <span
          v-for="(tag, index) in site.tags.slice(0, 5)"
          :key="index"
          class="rounded-full text-xs py-1 px-2 bg-gray-500"
          >{{ tag.name }}</span
        >
      </div>
    </div>
  </div>
</template>

<style scoped>
.site-card {
  background-color: #222;
}
</style>
