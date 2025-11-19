<script setup>
// Este componente sirve para crear la instancia de ImageCarousel con las imágenes y datos de las provincias, las imágenes no van a ser necesarias más adelante.

import ImageCarousel from './ImageCarousel.vue'
import { onMounted, reactive, ref } from 'vue'
import { getSites } from '@/api/sites'

const slides = reactive([])

const sitioBuenosAires = reactive({})
const sitioSalta = reactive({})
const sitioMendoza = reactive({})
const sitioTucuman = reactive({})

const loading = ref(true)

async function fetchSitios() {
  try {
    // Obtengo el primer sitio de la provincia y le agrego una imagen.
    sitioBuenosAires.value = await getSites({ province: 'Buenos Aires' })
    sitioBuenosAires.value = sitioBuenosAires.value.data[0]
    sitioBuenosAires.value.image =
      'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Frente_Iglesia_Catedral_desde_Plaza_Moreno.JPG/800px-Frente_Iglesia_Catedral_desde_Plaza_Moreno.JPG'

    sitioSalta.value = await getSites({ province: 'Salta' })
    console.log(sitioSalta.value)
    sitioSalta.value = sitioSalta.value.data[0]
    sitioSalta.value.image =
      'https://upload.wikimedia.org/wikipedia/commons/8/8e/Catedral_de_Salta_1.jpg'

    sitioMendoza.value = await getSites({ province: 'Mendoza' })
    sitioMendoza.value = sitioMendoza.value.data[0]
    sitioMendoza.value.image =
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Mendoza_-_Park_gate.jpg/1280px-Mendoza_-_Park_gate.jpg'

    sitioTucuman.value = await getSites({ province: 'Tucumán' })
    sitioTucuman.value = sitioTucuman.value.data[0]
    sitioTucuman.value.image =
      'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tucuman-CasaIndependencia2.jpg/1280px-Tucuman-CasaIndependencia2.jpg'

    slides.value = [
      {
        // Esta imagen es la que aparece de fondo
        src: 'https://www.argentina.gob.ar/sites/default/files/caba-puerto-madero.jpg',
        alt: 'Paisaje 1',
        caption: { title: 'Buenos Aires', subtitle: 'Argentina' },
        sitio: sitioBuenosAires.value,
      },
      {
        src: 'https://cloudfront-us-east-1.images.arcpublishing.com/infobae/OKXMUV72IRDLLJOZI3PM27X3ZQ.jpg',
        alt: 'Paisaje 2',
        caption: { title: 'Salta', subtitle: 'Argentina' },
        sitio: sitioSalta.value,
      },
      {
        src: 'https://resizer.iproimg.com/unsafe/1920x/filters:format(webp):quality(75):max_bytes(102400)/https://assets.iprofesional.com/assets/jpg/2024/11/587935.jpg',
        alt: 'Paisaje 3',
        caption: { title: 'Mendoza', subtitle: 'Argentina' },
        sitio: sitioMendoza.value,
      },
      {
        src: 'https://resizer.glanacion.com/resizer/v2/la-capilla-neogotica-de-villa-nougues-es-el-hito-HNRDYIWN7RCYBHZ53OIPX2DNAM.jpg?auth=999111d7897db4a04250624b012d70dd8e29c582b463a89ae7f0e05afcdd2538&width=1920&height=1282&quality=70&smart=true',
        alt: 'Paisaje 4',
        caption: { title: 'Tucumán', subtitle: 'Argentina' },
        sitio: sitioTucuman.value,
      },
    ]
  } catch (error) {
    console.error('Error fetching sitios for provinces carousel:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSitios()
})
</script>

<template>
  <div v-if="loading" class="flex h-full items-center justify-center py-12">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-600">Cargando...</p>
    </div>
  </div>
  <ImageCarousel
    v-else
    :images="slides.value"
    :autoplay="true"
    :interval="4000"
    :loop="true"
    :show-indicators="true"
    :show-arrows="true"
    :pause-on-hover="false"
    aria-label="Carrusel de provincias"
  />
</template>

<style scoped></style>
