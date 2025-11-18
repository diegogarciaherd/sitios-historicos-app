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
import { LMap, LTileLayer, LMarker, LCircle } from "@vue-leaflet/vue-leaflet"
import { getSitesNearby } from "@/api/sites.js"

const emit = defineEmits(["nearby-sites"])

// CONFIG
const zoom = ref(14)
const center = ref([-34.9225, -57.9531])

const radius = ref(5)
const selectedLocation = ref(null)

const radiusMeters = computed(() => radius.value * 1000)

// Limpiar selección + reiniciar posición del mapa
function clearSelection() {
  selectedLocation.value = null
  emit("nearby-sites", []) // limpiar resultados en el padre
}

// Evento de click en el mapa
async function onMapClick(e) {
  const { lat, lng } = e.latlng
  selectedLocation.value = { lat, lng }

  console.log("📍 Usuario seleccionó:", lat, lng)

  try {
    const sites = await getSitesNearby({
      lat, 
      lng, 
      radius: radius.value
    })

    console.log("📌 Sitios dentro del radio:", sites)

    //  Enviar los sitios al componente padre
    emit("nearby-sites", sites.data)

  } catch (err) {
    console.error("Error al obtener sitios cercanos:", err)
  }
}
</script>
