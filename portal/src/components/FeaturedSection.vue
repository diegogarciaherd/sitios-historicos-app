<script setup>
import SitesCarousel from './SitesCarousel.vue'
import SiteCarouselButton from './SiteCarouselButton.vue'
import SiteGrid from './SiteGrid.vue'
import { ref } from 'vue'

const featuredSites = [
  {
    id: 1,
    nombre: 'Casa Rosada',
    descripcion: 'Sede del Poder Ejecutivo Nacional',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg/1920px-Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg',
    ciudad: 'Buenos Aires',
    provincia: 'Buenos Aires',
    estado: 'Bueno',
    tags: ['histórico', 'gobierno', 'cultural', 'arquitectura', 'turismo', 'monumento'],
  },
  {
    id: 2,
    nombre: 'Catedral de Salta',
    descripcion: 'Catedral de la ciudad de Salta',
    image: 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Catedral_de_Salta_1.jpg',
    ciudad: 'Salta',
    provincia: 'Salta',
    estado: 'Bueno',
    tags: ['histórico', 'religioso'],
  },
  {
    id: 3,
    nombre: 'Parque General San Martín',
    descripcion: 'Un hermoso parque en la ciudad de Mendoza',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Mendoza_-_Park_gate.jpg/1280px-Mendoza_-_Park_gate.jpg',
    ciudad: 'Mendoza',
    provincia: 'Mendoza',
    estado: 'Regular',
    tags: ['natural', 'parque'],
  },
  {
    id: 4,
    nombre: 'Casa Histórica de la Independencia',
    descripcion: 'Lugar donde se declaró la independencia de Argentina',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tucuman-CasaIndependencia2.jpg/1280px-Tucuman-CasaIndependencia2.jpg',
    ciudad: 'San Miguel de Tucumán',
    provincia: 'Tucumán',
    estado: 'Malo',
    tags: ['histórico', 'cultural'],
  },
  {
    id: 5,
    nombre: 'Teatro Colón',
    descripcion: 'Uno de los teatros de ópera más importantes del mundo',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Frente_del_Teatro_Col%C3%B3n.jpg/1280px-Frente_del_Teatro_Col%C3%B3n.jpg',
    ciudad: 'Buenos Aires',
    provincia: 'Buenos Aires',
    estado: 'Bueno',
    tags: ['histórico', 'cultural'],
  },
  {
    id: 6,
    nombre: 'Ruinas de San Ignacio Miní',
    descripcion: 'Antigua misión jesuítica en Misiones',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Ruins_of_San_Ignacio_Miní_-_Church_2.jpg/1280px-Ruins_of_San_Ignacio_Miní_-_Church_2.jpg',
    ciudad: 'San Ignacio',
    provincia: 'Misiones',
    estado: 'Regular',
    tags: ['histórico', 'arqueológico', 'religioso'],
  },
  {
    id: 7,
    nombre: 'Cerro de los Siete Colores',
    descripcion: 'Formación geológica única en Purmamarca',
    image:
      'https://turismo-en-argentina.com/wp-content/uploads/2020/07/14074819238_6c00f7f002_o.jpg',
    ciudad: 'Purmamarca',
    provincia: 'Jujuy',
    estado: 'Bueno',
    tags: ['natural', 'geológico', 'turismo'],
  },
  {
    id: 8,
    nombre: 'Estancia Jesuítica de Alta Gracia',
    descripcion: 'Patrimonio de la Humanidad en Córdoba',
    image:
      'https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Altagracia%2C_Córdoba%2C_Argentina_-_panoramio_%281%29.jpg/1280px-Altagracia%2C_Córdoba%2C_Argentina_-_panoramio_%281%29.jpg',
    ciudad: 'Alta Gracia',
    provincia: 'Córdoba',
    estado: 'Regular',
    tags: ['histórico', 'cultural', 'religioso'],
  },
  {
    id: 9,
    nombre: 'Quebrada de Humahuaca',
    descripcion: 'Valle montañoso en Jujuy',
    image:
      'https://www.wendywutours.com/resource/upload/2008/banner-quebrada-de-humahuaca-2x.jpg.webp',
    ciudad: 'Humahuaca',
    provincia: 'Jujuy',
    estado: 'Bueno',
    tags: ['natural', 'geológico', 'turismo'],
  },
  {
    id: 10,
    nombre: 'Salto Alegre',
    descripcion: 'Impresionante cascada en la provincia de Misiones',
    image: 'https://www.cadena3.com/admin/playerswf/fotos/ARCHI_903796.jpg',
    ciudad: 'Aristóbulo del Valle',
    provincia: 'Misiones',
    estado: 'Bueno',
    tags: ['natural', 'turismo'],
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

const emptyArray = []
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
        <SiteCarouselButton :key="3" v-model="selectedCarousel" :value="3" :label="'Favoritos'" />
      </div>
      <div class="carousel-stack">
        <SitesCarousel
          v-for="option in carouselOptions"
          :key="`carousel-${option.id}`"
          v-show="selectedCarousel === option.id"
          :sites="option.sites"
          :autoplay="false"
        />
        <SiteGrid
          v-if="selectedCarousel === 3"
          :sites="featuredSites"
          :cols="4"
          :items-per-page="8"
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
