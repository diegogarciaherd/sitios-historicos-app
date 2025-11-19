<script setup>
import Topbar from '@/components/Topbar.vue'
import ProvincesCarousel from '@/components/ProvincesCarousel.vue'
import FeaturedSection from '@/components/FeaturedSection.vue'
import SiteViewCarousel from '@/components/SiteViewCarousel.vue'

const images = [
  {
    src: 'https://www.argentina.gob.ar/sites/default/files/caba-puerto-madero.jpg',
    alt: 'Paisaje 1',
  },
  {
    src: 'https://cloudfront-us-east-1.images.arcpublishing.com/infobae/OKXMUV72IRDLLJOZI3PM27X3ZQ.jpg',
    alt: 'Paisaje 2',
  },
  {
    src: 'https://resizer.iproimg.com/unsafe/1920x/filters:format(webp):quality(75):max_bytes(102400)/https://assets.iprofesional.com/assets/jpg/2024/11/587935.jpg',
    alt: 'Paisaje 3',
  },
  {
    src: 'https://resizer.glanacion.com/resizer/v2/la-capilla-neogotica-de-villa-nougues-es-el-hito-HNRDYIWN7RCYBHZ53OIPX2DNAM.jpg?auth=999111d7897db4a04250624b012d70dd8e29c582b463a89ae7f0e05afcdd2538&width=1920&height=1282&quality=70&smart=true',
    alt: 'Paisaje 4',
  },
]
</script>

<template>
  <Topbar />
  <main style="padding: 1rem; max-width: 1200px; margin: 0 auto" class="w-screen h-screen">
    <ProvincesCarousel />
  </main>
  <FeaturedSection />
  <div class="pb-16">
    <SiteViewCarousel :images="images" />
  </div>
</template>

<style scoped></style>
