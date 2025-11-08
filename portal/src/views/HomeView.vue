<script setup>
import Topbar from '@/components/Topbar.vue'
import ProvincesCarousel from '@/components/ProvincesCarousel.vue'
import FeaturedSection from '@/components/FeaturedSection.vue'
</script>

<template>
  <Topbar />
  <main style="padding: 1rem; max-width: 1200px; margin: 0 auto" class="w-screen h-screen">
    <ProvincesCarousel />
  </main>
  <FeaturedSection />
</template>

<style scoped></style>
