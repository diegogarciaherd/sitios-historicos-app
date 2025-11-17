<template>
    <div class="rounded-xl shadow bg-white p-2 w-full h-80">
      <l-map
        ref="mapRef"
        :zoom="zoom"
        :center="center"
        class="w-full h-full rounded-lg overflow-hidden"
      >
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </l-map>
    </div>
  </template>
  
  <script>
  import { LMap, LTileLayer } from "@vue-leaflet/vue-leaflet";
  
  export default {
    components: { LMap, LTileLayer },
    data() {
      return {
        zoom: 4,
        center: [-38.4161, -63.6167],
      };
    },
    mounted() {
      setTimeout(() => {
        if (this.$refs.mapRef?.leafletObject) {
          this.$refs.mapRef.leafletObject.invalidateSize();
        }
      }, 300);
    },
  };
  </script>
  
  <style>
  .leaflet-container {
    width: 100%;
    height: 100%;
  }
  </style>
  