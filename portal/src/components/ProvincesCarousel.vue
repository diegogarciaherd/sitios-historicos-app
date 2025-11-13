<script setup>
import ImageCarousel from './ImageCarousel.vue'
import { onMounted, reactive, ref } from 'vue'
import { getSites } from '@/api/sites'

const slides = reactive([])

const sitioBuenosAires = reactive({})
const sitioSalta = reactive({})
const sitioMendoza = reactive({})

async function fetchSitios() {
  sitioBuenosAires.value = await getSites({ province: 'Buenos Aires' })
  sitioBuenosAires.value = sitioBuenosAires.value[0]
  sitioBuenosAires.value.image =
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg/1920px-Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg'

  sitioSalta.value = await getSites({ province: 'Salta' })
  sitioSalta.value = sitioSalta.value[0]
  sitioSalta.value.image =
    'https://upload.wikimedia.org/wikipedia/commons/8/8e/Catedral_de_Salta_1.jpg'

  sitioMendoza.value = await getSites({ province: 'Mendoza' })
  sitioMendoza.value = sitioMendoza.value[0]
  sitioMendoza.value.image =
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Mendoza_-_Park_gate.jpg/1280px-Mendoza_-_Park_gate.jpg'

  slides.value = [
    {
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
      src: 'https://www.argentina.gob.ar/sites/default/files/photo6uspa-ruta.jpeg',
      alt: 'Paisaje 3',
      caption: { title: 'Mendoza', subtitle: 'Argentina' },
      sitio: sitioMendoza.value,
    },
    {
      src: 'https://resizer.glanacion.com/resizer/v2/la-capilla-neogotica-de-villa-nougues-es-el-hito-HNRDYIWN7RCYBHZ53OIPX2DNAM.jpg?auth=999111d7897db4a04250624b012d70dd8e29c582b463a89ae7f0e05afcdd2538&width=1920&height=1282&quality=70&smart=true',
      alt: 'Paisaje 4',
      caption: { title: 'Tucumán', subtitle: 'Argentina' },
      sitio: {
        nombre: 'Casa Histórica de la Independencia',
        descripcionBreve: 'Lugar donde se declaró la independencia de Argentina',
        image:
          'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tucuman-CasaIndependencia2.jpg/1280px-Tucuman-CasaIndependencia2.jpg',
        ciudad: 'San Miguel de Tucumán',
      },
    },
  ]
}

onMounted(() => {
  fetchSitios()
})
</script>

<template>
  <ImageCarousel
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
