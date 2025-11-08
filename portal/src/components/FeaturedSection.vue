<script setup>
import SitesCarousel from './SitesCarousel.vue'
import SiteCarouselButton from './SiteCarouselButton.vue'
import { ref } from 'vue'

const featuredSites = [
  {
    nombre: 'Casa Rosada',
    descripcion: 'Sede del Poder Ejecutivo Nacional',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg/1920px-Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg',
    ciudad: 'Buenos Aires',
  },
  {
    nombre: 'Catedral de Salta',
    descripcion: 'Catedral de la ciudad de Salta',
    image: 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Catedral_de_Salta_1.jpg',
    ciudad: 'Salta',
  },
  {
    nombre: 'Parque General San Martín',
    descripcion: 'Un hermoso parque en la ciudad de Mendoza',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Mendoza_-_Park_gate.jpg/1280px-Mendoza_-_Park_gate.jpg',
    ciudad: 'Mendoza',
  },
  {
    nombre: 'Casa Histórica de la Independencia',
    descripcion: 'Lugar donde se declaró la independencia de Argentina',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tucuman-CasaIndependencia2.jpg/1280px-Tucuman-CasaIndependencia2.jpg',
    ciudad: 'San Miguel de Tucumán',
  },
  {
    nombre: 'Teatro Colón',
    descripcion: 'Uno de los teatros de ópera más importantes del mundo',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Frente_del_Teatro_Col%C3%B3n.jpg/1280px-Frente_del_Teatro_Col%C3%B3n.jpg',
    ciudad: 'Buenos Aires',
  },
]

const carouselOptions = [
  {
    id: 'top-rated',
    label: 'Mejor puntuados',
    sites: featuredSites,
  },
  {
    id: 'most-visited',
    label: 'Más visitados',
    sites: featuredSites.slice().reverse(),
  },
]

const selectedCarousel = ref(carouselOptions[0]?.id ?? null)
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
          v-for="option in carouselOptions"
          :key="option.id"
          v-model="selectedCarousel"
          :value="option.id"
          :label="option.label"
        />
      </div>
      <div class="carousel-stack">
        <SitesCarousel
          v-for="option in carouselOptions"
          :key="`carousel-${option.id}`"
          v-show="selectedCarousel === option.id"
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
