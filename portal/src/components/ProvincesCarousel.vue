<script setup>
import ImageCarousel from './ImageCarousel.vue'

// Ejemplo de uso con imágenes de muestra. Reemplaza con tus propias rutas/alt.
const slides = [
  {
    src: 'https://picsum.photos/id/1018/1200/675',
    alt: 'Paisaje 1',
    caption: { title: 'Buenos Aires', subtitle: 'Argentina' },
  },
  {
    src: 'https://picsum.photos/id/1015/1200/675',
    alt: 'Paisaje 2',
    caption: { title: 'Salta', subtitle: 'Argentina' },
  },
  {
    src: 'https://picsum.photos/id/1024/1200/675',
    alt: 'Paisaje 3',
    caption: { title: 'Mendoza', subtitle: 'Argentina' },
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

<style scoped>
/* Contenedor opcional para ajustar márgenes/padding locales */
</style>
