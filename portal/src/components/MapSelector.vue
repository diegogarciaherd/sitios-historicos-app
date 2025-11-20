<template>
  <div class="w-full bg-white rounded-xl shadow p-4 flex flex-col gap-4">

    <!-- Header -->
    <div class="flex flex-col gap-2">
      <h2 class="text-sm font-semibold text-gray-700">
        Seleccionar ubicación en el mapa
      </h2>
    </div>

    <!-- Controles: responsive -->
    <!-- En pantallas <768 muestra el mapa primero (order-1) y los controles abajo (order-2). -->
    <div class="w-full order-2 md:order-1">
      <div class="flex w-full flex-col md:flex-row md:items-center md:gap-3 gap-2 flex-wrap">
        <select
          v-model="radius"
          class="w-full md:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-300 focus:border-blue-700 outline-none"
        >
          <option value="5">Radio: 5 km</option>
          <option value="10">Radio: 10 km</option>
          <option value="25">Radio: 25 km</option>
          <option value="50">Radio: 50 km</option>
        </select>

        <button
          @click="clearSelection"
          class="w-full md:w-auto px-3 py-2 text-sm rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 transition whitespace-normal break-words"
        >
          Limpiar
        </button>

        <button
          @click="searchByMap"
          :disabled="!selectedLocation || searching"
          class="w-full md:w-auto px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition whitespace-normal break-words text-center md:text-left md:max-w-xs"
        >
          <span v-if="!searching">Buscar por localización</span>
          <span v-else>Buscando...</span>
        </button>
      </div>
    </div>

    <!-- Mapa -->
    <div class="relative w-full h-72 rounded-lg overflow-hidden order-1 md:order-2">
      <l-map
        :zoom="zoom"
        :center="center"
        class="w-full h-full"
        @click="onMapClick"
      >
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <!-- Marcador de selección -->
        <l-marker
          v-if="selectedLocation"
          :lat-lng="selectedLocation"
        />

        <!-- Marcadores de sitios dentro del radio (icono naranja) -->
        <l-marker
          v-for="site in sitesMarkers"
          :key="`site-marker-${site.id}`"
          :lat-lng="[site.lat, site.lng]"
          :icon="orangeIcon"
        >
          <l-popup>
            <div class="max-w-xs">
              <h3 class="font-semibold text-slate-900">{{ site.nombre }}</h3>
              <p v-if="site.ciudad" class="text-xs text-slate-600 mb-1">{{ site.ciudad }}</p>
            </div>
          </l-popup>
        </l-marker>

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
import { LMap, LTileLayer, LMarker, LCircle, LPopup } from "@vue-leaflet/vue-leaflet"
import { getSitesNearby } from '@/api/sites'
import L from 'leaflet'

// Icono default Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Icono naranja para sitios cercanos
const orangeIcon = L.icon({
  iconUrl: 'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-orange.png',
  iconRetinaUrl: 'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-2x-orange.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
})

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

const sitesMarkers = ref([])

async function fetchMarkers(lat, lng, rKm) {
  searching.value = true
  sitesMarkers.value = []
  try {
    const resp = await getSitesNearby({ lat, lng, radius: rKm, per_page: 200 })
    const payload = resp.data || {}
    sitesMarkers.value = payload.data || []
    // Emitir por si el padre quiere sincronizar
    emit('nearby-sites', sitesMarkers.value)
  } catch (err) {
    console.error('Error fetching markers nearby:', err)
    sitesMarkers.value = []
  } finally {
    searching.value = false
  }
}

// Limpiar selección + reiniciar posición del mapa
function clearSelection() {
  selectedLocation.value = null
  sitesMarkers.value = []
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
  // Pedir marcadores para mostrar en el mapa
  await fetchMarkers(lat, lng, radius.value)
}

// Si el componente se monta con lat/lng en la URL, cargar marcadores
if (route.query && route.query.lat && route.query.lng) {
  const initialLat = Number(route.query.lat)
  const initialLng = Number(route.query.lng)
  const initialRadius = route.query.radius ? Number(route.query.radius) : radius.value
  // establecer selección visual
  selectedLocation.value = { lat: initialLat, lng: initialLng }
  // cargar marcadores
  fetchMarkers(initialLat, initialLng, initialRadius)
}
</script>
