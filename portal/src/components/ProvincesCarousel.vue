<script setup>
import ImageCarousel from './ImageCarousel.vue'

const slides = [
  {
    src: 'https://www.argentina.gob.ar/sites/default/files/caba-puerto-madero.jpg',
    alt: 'Paisaje 1',
    caption: { title: 'Buenos Aires', subtitle: 'Argentina' },
    sitio: {
      nombre: 'Casa Rosada',
      descripcion: 'Sede del Poder Ejecutivo Nacional',
      image:
        'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg/1920px-Casa_Rosada%2C_Buenos_Aires%2C_Argentina.jpg',
      ciudad: 'Buenos Aires',
    },
  },
  {
    src: 'https://cloudfront-us-east-1.images.arcpublishing.com/infobae/OKXMUV72IRDLLJOZI3PM27X3ZQ.jpg',
    alt: 'Paisaje 2',
    caption: { title: 'Salta', subtitle: 'Argentina' },
    sitio: {
      nombre: 'Catedral de Salta',
      descripcion: 'Catedral de la ciudad de Salta',
      image: 'https://upload.wikimedia.org/wikipedia/commons/8/8e/Catedral_de_Salta_1.jpg',
      ciudad: 'Salta',
    },
  },
  {
    src: 'https://www.argentina.gob.ar/sites/default/files/photo6uspa-ruta.jpeg',
    alt: 'Paisaje 3',
    caption: { title: 'Mendoza', subtitle: 'Argentina' },
    sitio: {
      nombre: 'Parque General San Martín',
      descripcion: 'Un hermoso parque en la ciudad de Mendoza',
      image:
        'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Mendoza_-_Park_gate.jpg/1280px-Mendoza_-_Park_gate.jpg',
      ciudad: 'Mendoza',
    },
  },
  {
    src: 'https://resizer.glanacion.com/resizer/v2/la-capilla-neogotica-de-villa-nougues-es-el-hito-HNRDYIWN7RCYBHZ53OIPX2DNAM.jpg?auth=999111d7897db4a04250624b012d70dd8e29c582b463a89ae7f0e05afcdd2538&width=1920&height=1282&quality=70&smart=true',
    alt: 'Paisaje 4',
    caption: { title: 'Tucumán', subtitle: 'Argentina' },
    sitio: {
      nombre: 'Casa Histórica de la Independencia',
      descripcion: 'Lugar donde se declaró la independencia de Argentina',
      image:
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tucuman-CasaIndependencia2.jpg/1280px-Tucuman-CasaIndependencia2.jpg',
      ciudad: 'San Miguel de Tucumán',
    },
  },
]
</script>

<template>
  <ImageCarousel
    :images="slides"
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
