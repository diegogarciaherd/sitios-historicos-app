<script setup>
import SitesCarousel from './SitesCarousel.vue'
import SiteCarouselButton from './SiteCarouselButton.vue'
import { onBeforeMount, reactive, ref } from 'vue'
import { getSites } from '@/api/sites'

const featuredSites = ref([])
const carouselOptions = reactive([])
const selectedCarousel = ref()

onBeforeMount(async () => {
  featuredSites.value = await getSites({})
  console.log('Fetched sites:', featuredSites.value)
  carouselOptions.value = [
    {
      id: 'top-rated',
      label: 'Mejor puntuados',
      sites: featuredSites.value,
    },
    {
      id: 'most-visited',
      label: 'Más visitados',
      sites: featuredSites.value.slice().reverse(),
    },
    {
      id: 'new-additions',
      label: 'Nuevas incorporaciones',
      sites: featuredSites.value.slice(0, 5),
    },
    {
      id: 'favorites',
      label: 'Favoritos',
      sites: featuredSites.value.slice(3, 7).reverse(),
    },
  ]
  selectedCarousel.value = ref(carouselOptions.value[0]?.id ?? null)
  console.log('Carousel Options:', carouselOptions)
  console.log('Selected Carousel:', selectedCarousel.value)
})
</script>

<template>
  <section
    class="flex m-0 w-full min-h-screen items-center justify-center bg-white overflow-x-hidden"
  >
    <div class="text-center">
      <h2 class="text-4xl font-bold mb-4">Sitios Históricos Destacados</h2>
      <p class="text-lg text-gray-700">
        Explora algunos de los sitios históricos más emblemáticos de Argentina.
      </p>
      <div class="flex justify-center gap-3 mt-8">
        <SiteCarouselButton
          v-for="option in carouselOptions.value"
          :key="option.id"
          v-model="selectedCarousel.value"
          :value="option.id"
          :label="option.label"
        />
      </div>
      <div class="carousel-stack">
        <SitesCarousel
          v-for="option in carouselOptions.value"
          :key="`carousel-${option.id}`"
          v-show="selectedCarousel.value === option.id"
          :sites="option.sites"
          :autoplay="false"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.carousel-stack {
  position: relative;
  margin-top: 3rem;
}
</style>
