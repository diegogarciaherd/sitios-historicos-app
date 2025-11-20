<script setup>
import ProvincesCarousel from '@/components/ProvincesCarousel.vue'
import FeaturedSection from '@/components/FeaturedSection.vue'
</script>

<template>
  <component :is="isMobile ? 'TopbarPhone' : 'Topbar'" />
  <main style="padding: 1rem; max-width: 1200px; margin: 0 auto" class="w-screen h-screen">
    <ProvincesCarousel />
  </main>
  <FeaturedSection />
</template>

<style scoped></style>

<script>
import TopbarPhone from '@/components/TopbarPhone.vue'
import Topbar from '@/components/Topbar.vue'

export default {
  components: {
    TopbarPhone,
    Topbar,
  },
  data() {
    return {
      isMobile: false,
    }
  },
  mounted() {
    this.checkDeviceType()
    window.addEventListener('resize', this.checkDeviceType)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkDeviceType)
  },
  methods: {
    checkDeviceType() {
      this.isMobile = window.innerWidth <= 768 // Adjust breakpoint as needed
    },
  },
}
</script>
