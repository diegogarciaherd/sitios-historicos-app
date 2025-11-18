<template>
  <div class="rounded-xl shadow bg-white p-4 w-full h-80">
    <div class="mb-3">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Seleccionar ubicación en el mapa
      </label>

      <div class="flex gap-2 mb-2">
        <select 
          v-model="radius" 
          class="px-3 py-1 border border-gray-300 rounded text-sm"
        >
          <option value="5">Radio: 5km</option>
          <option value="10">Radio: 10km</option>
          <option value="25">Radio: 25km</option>
          <option value="50">Radio: 50km</option>
        </select>

        <button 
          @click="clearSelection"
          class="px-3 py-1 bg-gray-200 text-gray-700 rounded text-sm hover:bg-gray-300"
        >
          Limpiar
        </button>
        <button
          @click="searchByMap"
          :disabled="!selectedLocation || searching"
          class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          <span v-if="!searching">Búsqueda por mapa</span>
          <span v-else>Buscando...</span>
        </button>
      </div>
    </div>

    <l-map 
      :zoom="zoom"
      :center="center"
      class="w-full h-full rounded-lg overflow-hidden"
      @click="onMapClick"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <!-- 📍 Marker seleccionado -->
      <l-marker
        v-if="selectedLocation"
        :lat-lng="selectedLocation"
      />

      <!-- 🔵 Círculo del radio seleccionado -->
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

const radiusMeters = computed(() => radius.value * 1000)

// Limpiar selección + reiniciar posición del mapa
function clearSelection() {
  selectedLocation.value = null
  // Remove map-related query params so the app returns to normal filter mode
  const newQuery = { ...route.query }
  delete newQuery.lat
  delete newQuery.lng
  delete newQuery.radius
  delete newQuery.page
  router.replace({ query: Object.keys(newQuery).length > 0 ? newQuery : {} })
}

// Click en el mapa sólo selecciona la ubicación; la búsqueda se ejecuta con el botón
function onMapClick(e) {
  const { lat, lng } = e.latlng
  selectedLocation.value = { lat, lng }
  console.log("📍 Usuario seleccionó:", lat, lng)
}

// Ejecuta la búsqueda por mapa (estricta) sólo cuando el usuario lo solicita
async function searchByMap() {
  if (!selectedLocation.value) return
  // Build a strict query containing ONLY map params so the search is shareable
  const { lat, lng } = selectedLocation.value
  const q = {
    lat: String(lat),
    lng: String(lng),
    radius: String(radius.value),
    page: '1'
  }

  // Replace the route query with only the map filters (strict mode)
  // This makes the URL shareable and signals other components to use map results only
  router.replace({ query: q })
}

const searching = ref(false)
</script>
