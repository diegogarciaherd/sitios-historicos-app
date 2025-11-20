<template>
  <div class="w-full bg-white rounded-xl shadow p-4 flex flex-col gap-4">

    <!-- Header -->
    <div class="flex flex-col gap-2">
      <h2 class="text-sm font-semibold text-gray-700">
        Seleccionar ubicación en el mapa
      </h2>

      <!-- Controles -->
      <div class="flex gap-3 items-center">

        <select
          v-model="radius"
          class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-300 focus:border-blue-700 outline-none"
        >
          <option value="5">Radio: 5 km</option>
          <option value="10">Radio: 10 km</option>
          <option value="25">Radio: 25 km</option>
          <option value="50">Radio: 50 km</option>
        </select>

        <!-- Clear -->
        <button
          @click="clearSelection"
          class="px-1 py-1 text-sm rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 transition"
        >
          Limpiar
        </button>

        <!-- Search -->
        <button
          @click="searchByMap"
          :disabled="!selectedLocation || searching"
          class="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition"
        >
          <span v-if="!searching">Buscar por localizacion</span>
          <span v-else>Buscando...</span>
        </button>

      </div>
    </div>

    <!-- Mapa -->
    <div class="relative w-full h-72 rounded-lg overflow-hidden">
      <l-map
        :zoom="zoom"
        :center="center"
        class="w-full h-full"
        @click="onMapClick"
      >
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <l-marker
          v-if="selectedLocation"
          :lat-lng="selectedLocation"
        />

        <l-circle
          v-if="selectedLocation"
          :lat-lng="selectedLocation"
          :radius="radiusMeters"
          color="blue"
          fill-color="blue"
          :fill-opacity="0.1"
        />
      </l-map>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LMap, LTileLayer, LMarker, LCircle } from "@vue-leaflet/vue-leaflet"

const emit = defineEmits(["nearby-sites"])
const router = useRouter()
const route = useRoute()

// CONFIG
const zoom = ref(14)
const center = ref([-34.9225, -57.9531])

const radius = ref(5)
const selectedLocation = ref(null)
const searching = ref(false)

const radiusMeters = computed(() => radius.value * 1000)

// Limpiar selección + reiniciar posición del mapa
function clearSelection() {
  selectedLocation.value = null
  const newQuery = { ...route.query }
  delete newQuery.lat
  delete newQuery.lng
  delete newQuery.radius
  delete newQuery.page
  router.replace({ query: Object.keys(newQuery).length > 0 ? newQuery : {} })
}

// Solo selecciona la ubicación
function onMapClick(e) {
  const { lat, lng } = e.latlng
  selectedLocation.value = { lat, lng }
}

// Ejecuta la búsqueda
async function searchByMap() {
  if (!selectedLocation.value) return
  
  const { lat, lng } = selectedLocation.value
  const q = {
    lat: String(lat),
    lng: String(lng),
    radius: String(radius.value),
    page: '1'
  }

  router.replace({ query: q })
}
</script>
