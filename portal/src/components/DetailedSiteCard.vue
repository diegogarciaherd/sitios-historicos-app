<script setup>
const props = defineProps({
  site: {
    type: Object,
    required: true,
  },
})

const stateColors = {
  Bueno: 'badge-success',
  Regular: 'badge-warning',
  Malo: " [--badge-color:red]",
}
</script>

<template>
  <div
  class="site-card relative rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300 w-full aspect-[4/5]"
>
  <img
    :src="site.image"
    :alt="site.nombre"
    class="absolute inset-0 w-full h-full object-cover z-0"
  />

  <div
    class="absolute bottom-0 p-4 text-start text-white bg-gradient-to-t from-gray-800 to-transparent w-full z-10"
  >
    <h2 class="text-large font-semibold mb-2">{{ site.nombre }}</h2>
    <p class="mb-2 text-sm">{{ site.descripcionBreve }}</p>
    <p class="mb-2 text-sm">{{ site.ciudad }} | {{ site.provincia }}</p>

    <span
      class="badge badge-dash badge-primary"
      :class="stateColors[site.estado] || 'badge'"
    >
      {{ site.estado }}
    </span>

    <div class="flex mt-2 space-2 flex-wrap max-h-14 items-end">
      <span
        v-for="(tag, index) in site.tags.slice(0, 5)"
        :key="index"
        class="rounded-full text-xs py-1 px-2 bg-gray-500"
      >
        {{ tag.name }}
      </span>
    </div>
  </div>
</div>
</template>