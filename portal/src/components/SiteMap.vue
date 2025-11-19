<script setup>
import { LMap, LTileLayer, LMarker, LTooltip } from "@vue-leaflet/vue-leaflet"
import "leaflet/dist/leaflet.css"
import { ref, watch } from "vue"

// Solución para los iconos rotos de Leaflet
import L from "leaflet"

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const props = defineProps({
  lat: {
    type: Number,
    required: true
  },
  lng: {
    type: Number,
    required: true
  },
  nombre: {
    type: String,
    required: true
  },
  descripcionBreve: {
    type: String,
    default: ""
  },
  ciudad: {
    type: String,
    default: ""
  }
})

const center = ref([props.lat, props.lng])
const zoom = ref(14) // Zoom más adecuado para ver la ciudad/localidad
const map = ref()

// Watcher para actualizar cuando cambien las props
watch(() => [props.lat, props.lng, props.nombre], ([newLat, newLng]) => {
  if (newLat && newLng) {
    center.value = [newLat, newLng]
  }
})

// Función para cuando el mapa esté listo
function onMapReady(mapObject) {
  map.value = mapObject
  // Asegurar que el mapa se redimensiona correctamente
  setTimeout(() => {
    mapObject.invalidateSize()
  }, 100)
}
</script>

<template>
  <div class="w-full h-64 rounded-lg overflow-hidden bg-slate-800">
    <l-map 
      ref="map"
      :zoom="zoom" 
      :center="center"
      :use-global-leaflet="false"
      @ready="onMapReady"
      class="w-full h-full"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      ></l-tile-layer>
      
      <l-marker :lat-lng="center">
        <l-tooltip :options="{ permanent: false, direction: 'top' }">
          <div class="max-w-xs">
            <h3 class="font-semibold text-slate-900">{{ nombre }}</h3>
            <p v-if="ciudad" class="text-xs text-slate-600 mb-1">{{ ciudad }}</p>
            <p v-if="descripcionBreve" class="text-sm text-slate-700 mt-1">
              {{ descripcionBreve }}
            </p>
          </div>
        </l-tooltip>
      </l-marker>
    </l-map>
  </div>
</template>

<style>
.leaflet-container {
  background: #1e293b;
  font-family: inherit;
}

/* Estilos personalizados para el tooltip */
.leaflet-tooltip {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.leaflet-tooltip-top:before {
  border-top-color: #cbd5e1;
}
</style>