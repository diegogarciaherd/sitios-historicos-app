<script setup>
import { onMounted, ref, watch } from "vue"
import L from "leaflet"

const props = defineProps({
  lat: Number,
  lng: Number,
})

const map = ref(null)
const mapElement = ref(null)

function initMap() {
  if (!props.lat || !props.lng) return

  map.value = L.map(mapElement.value).setView([props.lat, props.lng], 15)

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap"
  }).addTo(map.value)

  L.marker([props.lat, props.lng]).addTo(map.value)
}

watch(() => [props.lat, props.lng], initMap)
onMounted(initMap)
</script>

<template>
  <div ref="mapElement" class="w-full h-64 rounded-lg overflow-hidden"></div>
</template>

<style>
.leaflet-container {
  width: 100%;
  height: 100%;
}
</style>
